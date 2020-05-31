import pandas as pd
import numpy as np
import glob
import re
from datetime import date, timedelta
import time
import io
import requests
import sys


def save_from_web(url):
    url = r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/{}'.format(url)
    raw_string = requests.get(url).content
    return pd.read_csv(io.StringIO(raw_string.decode('utf-8')))

def load_time_series(source='web', update='manual'):
    if source == 'web':
        today = date.today()
        prepend = r'csse_covid_19_time_series/time_series_covid19_'
        current_data = False
        start_time = time.time()
        # Continuously re-download files until all have been updated
        while not current_data:
            try:
                confirmed_us = save_from_web(r'{}confirmed_US.csv'.format(prepend))
                print('confirmed_us      ', confirmed_us.columns[-1])
                confirmed_global = save_from_web(r'{}confirmed_global.csv'.format(prepend))
                print('confirmed_global  ', confirmed_global.columns[-1])
                deaths_us = save_from_web(r'{}deaths_US.csv'.format(prepend))
                print('deaths_us         ', deaths_us.columns[-1])
                deaths_global = save_from_web(r'{}deaths_global.csv'.format(prepend))
                print('deaths_global     ', deaths_global.columns[-1])
                recovered_global =save_from_web(r'{}recovered_global.csv'.format(prepend))
                print('recovered_global  ', recovered_global.columns[-1])

                csv_files = {'1': confirmed_us,
                            '2': confirmed_global,
                            '3': deaths_us,
                            '4': deaths_global,
                            '5': recovered_global}

                responses = {'1': False,
                            '2': False,
                            '3': False,
                            '4': False,
                            '5': False}

                for csv in csv_files:
                    if pd.to_datetime(csv_files[csv].columns[-1]) == today:
                        responses[csv] = True

                if sum(responses.values()) == 5:
                    current_data = True
                    print()
                    print('Date = {}'.format(confirmed_us.columns[-1]))
                elif update == 'manual':
                    current_data = True
                    print()
                    print('Date = {}'.format(confirmed_us.columns[-1]))
                else:
                    if time.time() - start_time > 2.5 * 3600:  # stop checking after 2.5 hours
                        print()
                        print('Timed out after 2.5 hours')
                        return 'end'
                    print()
                    print('Waiting for GitHub update...')
                    time.sleep(600)
                    print()
            except requests.exceptions.ConnectionError:
                if time.time() - start_time > 2.5 * 3600:  # stop checking after 2.5 hours
                    print()
                    print('Timed out after 2.5 hours')
                    return 'end'
                print()
                print('Waiting for connection to internet...')
                time.sleep(600)
                print()
        
        confirmed_us.to_csv('data/raw/time_series_covid19_confirmed_US.csv', index=False)
        confirmed_global.to_csv('data/raw/time_series_covid19_confirmed_global.csv', index=False)
        deaths_us.to_csv('data/raw/time_series_covid19_deaths_us.csv', index=False)
        deaths_global.to_csv('data/raw/time_series_covid19_deaths_global.csv', index=False)
        recovered_global.to_csv('data/raw/time_series_covid19_recovered_global.csv', index=False)

    elif source == 'folder':
        confirmed_us = pd.read_csv('data/raw/time_series_covid19_confirmed_US.csv')
        confirmed_global = pd.read_csv('data/raw/time_series_covid19_confirmed_global.csv')
        deaths_us = pd.read_csv('data/raw/time_series_covid19_deaths_us.csv')
        deaths_global = pd.read_csv('data/raw/time_series_covid19_deaths_global.csv')
        recovered_global = pd.read_csv('data/raw/time_series_covid19_recovered_global.csv')

    dates = []
    for column in confirmed_global.columns:
        if re.search(r'([0-9]{1,2}\/[0-9]{1,2}\/(20))', column):
            dates.append(column)

    print()
    print('Transforming data')
    # Melt (de-pivot), join, and union the above tables
    confirmed_us_melt = pd.melt(
        confirmed_us,
        id_vars=['Country_Region', 'Province_State', 'Admin2', 'Lat', 'Long_'],
        value_vars=dates).rename(columns={'Country_Region': 'Country/Region',
                                        'Province_State': 'Province/State',
                                        'Lat': 'Latitude',
                                        'Long_': 'Longitude',
                                        'variable': 'date',
                                        'value': 'Confirmed'})

    deaths_us_melt = pd.melt(
        deaths_us,
        id_vars=['Country_Region', 'Province_State', 'Admin2', 'Lat', 'Long_'],
        value_vars=dates).rename(columns={'Country_Region': 'Country/Region',
                                        'Province_State': 'Province/State',
                                        'Lat': 'Latitude',
                                        'Long_': 'Longitude',
                                        'variable': 'date',
                                        'value': 'Deaths'})

    us_confirmed_deaths = pd.merge(
        confirmed_us_melt,
        deaths_us_melt[['date',
                        'Country/Region',
                        'Province/State',
                        'Admin2',
                        'Deaths']],
        on=['date',
            'Country/Region',
            'Province/State',
            'Admin2'],
        how='outer').assign(Recovered=np.nan)[['date',
                                               'Country/Region',
                                               'Province/State',
                                               'Admin2',
                                               'Latitude',
                                               'Longitude',
                                               'Confirmed',
                                               'Deaths',
                                               'Recovered']]

    confirmed_global_melt = pd.melt(
        confirmed_global,
        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
        value_vars=dates).rename(columns={'Lat': 'Latitude',
                                        'Long': 'Longitude',
                                        'variable': 'date',
                                        'value': 'Confirmed'}).assign(Admin2=np.nan)

    # aggregate Canada confirmed because recovered is not aggregated
    confirmed_canada = confirmed_global_melt[confirmed_global_melt['Country/Region'] == 'Canada'].groupby('date', as_index=False).agg({'Confirmed': 'sum'})
    confirmed_canada['Country/Region'] = 'Canada'
    confirmed_canada['Province/State'] = np.nan
    confirmed_canada['Latitude'] = 56.1304
    confirmed_canada['Longitude'] = -106.346800
    confirmed_canada['Admin2'] = np.nan
    confirmed_canada = confirmed_canada[['Country/Region', 'Province/State', 'Latitude', 'Longitude', 'date', 'Confirmed', 'Admin2']]

    confirmed_global_melt = pd.concat([
        confirmed_global_melt[confirmed_global_melt['Country/Region'] != 'Canada'],
        confirmed_canada])

    deaths_global_melt = pd.melt(deaths_global,
        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
        value_vars=dates).rename(columns={'Lat': 'Latitude',
                                        'Long': 'Longitude',
                                        'variable': 'date',
                                        'value': 'Deaths'}).assign(Admin2=np.nan)

    # aggregate Canada deaths because recovered is not aggregated
    deaths_canada = deaths_global_melt[deaths_global_melt['Country/Region'] == 'Canada'].groupby('date', as_index=False).agg({'Deaths': 'sum'})
    deaths_canada['Country/Region'] = 'Canada'
    deaths_canada['Province/State'] = np.nan
    deaths_canada['Latitude'] = 56.1304
    deaths_canada['Longitude'] = -106.346800
    deaths_canada['Admin2'] = np.nan
    deaths_canada = deaths_canada[['Country/Region', 'Province/State', 'Latitude', 'Longitude', 'date', 'Deaths', 'Admin2']]

    deaths_global_melt = pd.concat([
        deaths_global_melt[deaths_global_melt['Country/Region'] != 'Canada'],
        deaths_canada])

    confirmed_deaths_global = pd.merge(
        confirmed_global_melt,
        deaths_global_melt[['date',
                            'Country/Region',
                            'Province/State',
                            'Admin2',
                            'Deaths']],
        on=['date', 'Country/Region', 'Province/State', 'Admin2'],
        how='outer')

    # fix some mismatched coordinates
    confirmed_deaths_global.loc[confirmed_deaths_global['Country/Region'] == 'Syria', ['Latitude']] = 34.802075
    confirmed_deaths_global.loc[confirmed_deaths_global['Country/Region'] == 'Syria', ['Longitude']] = 38.996815
    
    confirmed_deaths_global.loc[confirmed_deaths_global['Country/Region'] == 'Mozambique', ['Latitude']] = -18.6657
    confirmed_deaths_global.loc[confirmed_deaths_global['Country/Region'] == 'Mozambique', ['Longitude']] = 35.5296
    
    confirmed_deaths_global.loc[confirmed_deaths_global['Country/Region'] == 'Timor-Leste', ['Latitude']] = -8.8742
    confirmed_deaths_global.loc[confirmed_deaths_global['Country/Region'] == 'Timor-Leste', ['Longitude']] = 125.7275

    recovered_global_melt = pd.melt(
        recovered_global,
        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
        value_vars=dates).rename(columns={'Lat': 'Latitude',
                                        'Long': 'Longitude',
                                        'variable': 'date',
                                        'value': 'Recovered'}).assign(Admin2=np.nan)

    # fix some mismatched coordinates
    recovered_global_melt.loc[recovered_global_melt['Country/Region'] == 'Syria', ['Latitude']] = 34.802075
    recovered_global_melt.loc[recovered_global_melt['Country/Region'] == 'Syria', ['Longitude']] = 38.996815
    
    recovered_global_melt.loc[recovered_global_melt['Country/Region'] == 'Mozambique', ['Latitude']] = -18.6657
    recovered_global_melt.loc[recovered_global_melt['Country/Region'] == 'Mozambique', ['Longitude']] = 35.5296
    
    recovered_global_melt.loc[recovered_global_melt['Country/Region'] == 'Timor-Leste', ['Latitude']] = -8.8742
    recovered_global_melt.loc[recovered_global_melt['Country/Region'] == 'Timor-Leste', ['Longitude']] = 125.7275

    global_confirmed_deaths_recovered = pd.merge(
        confirmed_deaths_global,
        recovered_global_melt[['date',
                               'Country/Region',
                               'Province/State',
                               'Admin2',
                               'Recovered']],
        on=['date', 'Country/Region', 'Province/State', 'Admin2'],
        how='outer')[['date',
                    'Country/Region',
                    'Province/State',
                    'Admin2',
                    'Latitude',
                    'Longitude',
                    'Confirmed',
                    'Deaths',
                    'Recovered']]

    df = pd.concat([
        us_confirmed_deaths,
        global_confirmed_deaths_recovered
    ])

    df['date'] = pd.to_datetime(df['date'])

    # Create "Recovered" state for unassigned recoveries
    df.loc[(df['Country/Region'] == 'US') & (df['Recovered'].notna()), 'Province/State'] = 'Recovered'
    df.loc[df['Province/State'] == 'Recovered', 'Confirmed'] = 0
    df.loc[df['Province/State'] == 'Recovered', 'Deaths'] = 0
    df['Recovered'] = df['Recovered'].fillna(0)

    # Create "Active" column
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']
    df.loc[df['Province/State'] == 'Recovered', 'Active'] = 0

    df['Recovered'] = df['Recovered'].astype(int)
    df['Active'] = df['Active'].astype(int)

    df = df.sort_values(by=['date', 'Country/Region', 'Province/State', 'Admin2']).reset_index(drop=True)

    # Rename countries
    df['Country/Region'].replace('Korea, South', 'South Korea', inplace=True)
    df['Country/Region'].replace('Taiwan*', 'Taiwan', inplace=True)

    return df

def load_daily_reports(source='web'):
    if source=='web':
        # Load files from web
        file_date = date(2020, 1, 22)
        dates = []

        while file_date <= date.today():
            dates.append(file_date)
            file_date += timedelta(days=1)
            
        files = []
        for file in dates:
            file = file.strftime("%m-%d-%Y")
            url = r'csse_covid_19_daily_reports/{}.csv'.format(file)
            raw_string = requests.get(url).content
            df = pd.read_csv(io.StringIO(raw_string.decode('utf-8')))
            if b'404: Not Found' not in raw_string:
                df.to_csv('data/raw/{}.csv'.format(file), index=False)
                print(file)
            df['date'] = pd.to_datetime(file)
            df.rename(columns={'Province_State': 'Province/State',
                               'Country_Region': 'Country/Region',
                               'Lat': 'Latitude',
                               'Long_': 'Longitude'}, inplace=True)
            files.append(df)

    elif source=='folder':
        # Load files from folder
        path = 'data/raw'
        all_files = glob.glob(path + "/*.csv")

        files = []

        for filename in all_files:
            file = re.search(r'([0-9]{2}\-[0-9]{2}\-[0-9]{4})', filename)[0]
            print(file)
            df = pd.read_csv(filename, index_col=None, header=0)
            df['date'] = pd.to_datetime(file)
            df.rename(columns={'Province_State': 'Province/State',
                               'Country_Region': 'Country/Region',
                               'Lat': 'Latitude',
                               'Long_': 'Longitude'}, inplace=True)
            files.append(df)

    # Rename countries with duplicate naming conventions
    df['Country/Region'].replace('Mainland China', 'China', inplace=True)
    df['Country/Region'].replace('Hong Kong SAR', 'Hong Kong', inplace=True)
    df['Country/Region'].replace(' Azerbaijan', 'Azerbaijan', inplace=True)
    df['Country/Region'].replace('Holy See', 'Vatican City', inplace=True)
    df['Country/Region'].replace('Iran (Islamic Republic of)', 'Iran', inplace=True)
    df['Country/Region'].replace('Taiwan*', 'Taiwan', inplace=True)
    df['Country/Region'].replace('Korea, South', 'South Korea', inplace=True)
    df['Country/Region'].replace('Viet Nam', 'Vietnam', inplace=True)
    df['Country/Region'].replace('Macao SAR', 'Macau', inplace=True)
    df['Country/Region'].replace('Russian Federation', 'Russia', inplace=True)
    df['Country/Region'].replace('Republic of Moldova', 'Moldova', inplace=True)
    df['Country/Region'].replace('Czechia', 'Czech Republic', inplace=True)
    df['Country/Region'].replace('Congo (Kinshasa)', 'Congo', inplace=True)
    df['Country/Region'].replace('Northern Ireland', 'United Kingdom', inplace=True)
    df['Country/Region'].replace('Republic of Korea', 'South Korea', inplace=True)
    df['Country/Region'].replace('Congo (Brazzaville)', 'Congo', inplace=True)
    df['Country/Region'].replace('Taipei and environs', 'Taiwan', inplace=True)
    df['Country/Region'].replace('Others', 'Cruise Ship', inplace=True)
    df['Province/State'].replace('Cruise Ship', 'Diamond Princess cruise ship', inplace=True)
    df['Province/State'].replace('From Diamond Princess', 'Diamond Princess cruise ship', inplace=True)

    # Replace old reporting standards
    df['Province/State'].replace('Chicago', 'Illinois', inplace=True)
    df['Province/State'].replace('Chicago, IL', 'Illinois', inplace=True)
    df['Province/State'].replace('Cook County, IL', 'Illinois', inplace=True)
    df['Province/State'].replace('Boston, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace(' Norfolk County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Suffolk County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Middlesex County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Norwell County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Plymouth County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Norfolk County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Berkshire County, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Unknown Location, MA', 'Massachusetts', inplace=True)
    df['Province/State'].replace('Los Angeles, CA', 'California', inplace=True)
    df['Province/State'].replace('Orange, CA', 'California', inplace=True)
    df['Province/State'].replace('Santa Clara, CA', 'California', inplace=True)
    df['Province/State'].replace('San Benito, CA', 'California', inplace=True)
    df['Province/State'].replace('Humboldt County, CA', 'California', inplace=True)
    df['Province/State'].replace('Sacramento County, CA', 'California', inplace=True)
    df['Province/State'].replace('Travis, CA (From Diamond Princess)', 'California', inplace=True)
    df['Province/State'].replace('Placer County, CA', 'California', inplace=True)
    df['Province/State'].replace('San Mateo, CA', 'California', inplace=True)
    df['Province/State'].replace('Sonoma County, CA', 'California', inplace=True)
    df['Province/State'].replace('Berkeley, CA', 'California', inplace=True)
    df['Province/State'].replace('Orange County, CA', 'California', inplace=True)
    df['Province/State'].replace('Contra Costa County, CA', 'California', inplace=True)
    df['Province/State'].replace('San Francisco County, CA', 'California', inplace=True)
    df['Province/State'].replace('Yolo County, CA', 'California', inplace=True)
    df['Province/State'].replace('Santa Clara County, CA', 'California', inplace=True)
    df['Province/State'].replace('San Diego County, CA', 'California', inplace=True)
    df['Province/State'].replace('Travis, CA', 'California', inplace=True)
    df['Province/State'].replace('Alameda County, CA', 'California', inplace=True)
    df['Province/State'].replace('Madera County, CA', 'California', inplace=True)
    df['Province/State'].replace('Santa Cruz County, CA', 'California', inplace=True)
    df['Province/State'].replace('Fresno County, CA', 'California', inplace=True)
    df['Province/State'].replace('Riverside County, CA', 'California', inplace=True)
    df['Province/State'].replace('Shasta County, CA', 'California', inplace=True)
    df['Province/State'].replace('Seattle, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Snohomish County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('King County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Unassigned Location, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Clark County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Jefferson County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Pierce County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Kittitas County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Grant County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Spokane County, WA', 'Washington', inplace=True)
    df['Province/State'].replace('Tempe, AZ', 'Arizona', inplace=True)
    df['Province/State'].replace('Maricopa County, AZ', 'Arizona', inplace=True)
    df['Province/State'].replace('Pinal County, AZ', 'Arizona', inplace=True)
    df['Province/State'].replace('Madison, WI', 'Wisconsin', inplace=True)
    df['Province/State'].replace('San Antonio, TX', 'Texas', inplace=True)
    df['Province/State'].replace('Lackland, TX', 'Texas', inplace=True)
    df['Province/State'].replace('Lackland, TX (From Diamond Princess)', 'Texas', inplace=True)
    df['Province/State'].replace('Harris County, TX', 'Texas', inplace=True)
    df['Province/State'].replace('Fort Bend County, TX', 'Texas', inplace=True)
    df['Province/State'].replace('Montgomery County, TX', 'Texas', inplace=True)
    df['Province/State'].replace('Collin County, TX', 'Texas', inplace=True)
    df['Province/State'].replace('Ashland, NE', 'Nebraska', inplace=True)
    df['Province/State'].replace('Omaha, NE (From Diamond Princess)', 'Nebraska', inplace=True)
    df['Province/State'].replace('Douglas County, NE', 'Nebraska', inplace=True)
    df['Province/State'].replace('Portland, OR', 'Oregon', inplace=True)
    df['Province/State'].replace('Umatilla, OR', 'Oregon', inplace=True)
    df['Province/State'].replace('Klamath County, OR', 'Oregon', inplace=True)
    df['Province/State'].replace('Douglas County, OR', 'Oregon', inplace=True)
    df['Province/State'].replace('Marion County, OR', 'Oregon', inplace=True)
    df['Province/State'].replace('Jackson County, OR ', 'Oregon', inplace=True)
    df['Province/State'].replace('Washington County, OR', 'Oregon', inplace=True)
    df['Province/State'].replace('Providence, RI', 'Rhode Island', inplace=True)
    df['Province/State'].replace('Providence County, RI', 'Rhode Island', inplace=True)
    df['Province/State'].replace('Grafton County, NH', 'New Hampshire', inplace=True)
    df['Province/State'].replace('Rockingham County, NH', 'New Hampshire', inplace=True)
    df['Province/State'].replace('Hillsborough, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Sarasota, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Santa Rosa County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Broward County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Lee County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Volusia County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Manatee County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Okaloosa County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('Charlotte County, FL', 'Florida', inplace=True)
    df['Province/State'].replace('New York City, NY', 'New York', inplace=True)
    df['Province/State'].replace('Westchester County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Queens County, NY', 'New York', inplace=True)
    df['Province/State'].replace('New York County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Nassau, NY', 'New York', inplace=True)
    df['Province/State'].replace('Nassau County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Rockland County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Saratoga County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Suffolk County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Ulster County, NY', 'New York', inplace=True)
    df['Province/State'].replace('Fulton County, GA', 'Georgia', inplace=True)
    df['Province/State'].replace('Floyd County, GA', 'Georgia', inplace=True)
    df['Province/State'].replace('Polk County, GA', 'Georgia', inplace=True)
    df['Province/State'].replace('Cherokee County, GA', 'Georgia', inplace=True)
    df['Province/State'].replace('Cobb County, GA', 'Georgia', inplace=True)
    df['Province/State'].replace('Wake County, NC', 'North Carolina', inplace=True)
    df['Province/State'].replace('Chatham County, NC', 'North Carolina', inplace=True)
    df['Province/State'].replace('Bergen County, NJ', 'New Jersey', inplace=True)
    df['Province/State'].replace('Hudson County, NJ', 'New Jersey', inplace=True)
    df['Province/State'].replace('Clark County, NV', 'Nevada', inplace=True)
    df['Province/State'].replace('Washoe County, NV', 'Nevada', inplace=True)
    df['Province/State'].replace('Williamson County, TN', 'Tennessee', inplace=True)
    df['Province/State'].replace('Davidson County, TN', 'Tennessee', inplace=True)
    df['Province/State'].replace('Shelby County, TN', 'Tennessee', inplace=True)
    df['Province/State'].replace('Montgomery County, MD', 'Maryland', inplace=True)
    df['Province/State'].replace('Harford County, MD', 'Maryland', inplace=True)
    df['Province/State'].replace('Denver County, CO', 'Colorado', inplace=True)
    df['Province/State'].replace('Summit County, CO', 'Colorado', inplace=True)
    df['Province/State'].replace('Douglas County, CO', 'Colorado', inplace=True)
    df['Province/State'].replace('El Paso County, CO', 'Colorado', inplace=True)
    df['Province/State'].replace('Delaware County, PA', 'Pennsylvania', inplace=True)
    df['Province/State'].replace('Wayne County, PA', 'Pennsylvania', inplace=True)
    df['Province/State'].replace('Montgomery County, PA', 'Pennsylvania', inplace=True)
    df['Province/State'].replace('Fayette County, KY', 'Kentucky', inplace=True)
    df['Province/State'].replace('Jefferson County, KY', 'Kentucky', inplace=True)
    df['Province/State'].replace('Harrison County, KY', 'Kentucky', inplace=True)
    df['Province/State'].replace('Marion County, IN', 'Indiana', inplace=True)
    df['Province/State'].replace('Hendricks County, IN', 'Indiana', inplace=True)
    df['Province/State'].replace('Ramsey County, MN', 'Minnesota', inplace=True)
    df['Province/State'].replace('Carver County, MN', 'Minnesota', inplace=True)
    df['Province/State'].replace('Fairfield County, CT', 'Connecticut', inplace=True)
    df['Province/State'].replace('Charleston County, SC', 'South Carolina', inplace=True)
    df['Province/State'].replace('Spartanburg County, SC', 'South Carolina', inplace=True)
    df['Province/State'].replace('Kershaw County, SC', 'South Carolina', inplace=True)
    df['Province/State'].replace('Davis County, UT', 'Utah', inplace=True)
    df['Province/State'].replace('Honolulu County, HI', 'Hawaii', inplace=True)
    df['Province/State'].replace('Tulsa County, OK', 'Oklahoma', inplace=True)
    df['Province/State'].replace('Fairfax County, VA', 'Virginia', inplace=True)
    df['Province/State'].replace('St. Louis County, MO', 'Missouri', inplace=True)
    df['Province/State'].replace('Unassigned Location, VT', 'Vermont', inplace=True)
    df['Province/State'].replace('Bennington County, VT', 'Vermont', inplace=True)
    df['Province/State'].replace('Johnson County, IA', 'Iowa', inplace=True)
    df['Province/State'].replace('Jefferson Parish, LA', 'Louisiana', inplace=True)
    df['Province/State'].replace('Johnson County, KS', 'Kansas', inplace=True)
    df['Province/State'].replace('Washington, D.C.', 'District of Columbia', inplace=True)

    # Fill missing values as 0
    df['Confirmed'] = df['Confirmed'].fillna(0).astype(int)
    df['Deaths'] = df['Deaths'].fillna(0).astype(int)
    df['Recovered'] = df['Recovered'].fillna(0).astype(int)

    # Replace missing values for latitude and longitude
    df['Latitude'] = df['Latitude'].fillna(df.groupby('Province/State')['Latitude'].transform('mean'))
    df['Longitude'] = df['Longitude'].fillna(df.groupby('Province/State')['Longitude'].transform('mean'))

    return pd.concat(files, axis=0, ignore_index=True, sort=False)

def etl(layout='time_series', source='web', update='manual'):
    if layout == 'time_series':
        df = load_time_series(source=source, update=update)
        if isinstance(df, str):
            return df
    elif layout == 'daily_reports':
        df = load_daily_reports(source=source)

    # create Active cases column
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']

    # Re-order the columns for readability
    df = df[['date',
            'Country/Region',
            'Province/State',
            'Admin2',
            'Latitude',
            'Longitude',
            'Confirmed',
            'Active',
            'Deaths',
            'Recovered']]

    return df

def worldwide(data):
    print('processing worldwide')
    df = data.groupby(['date', 'Country/Region'], as_index=False).agg({'Latitude': 'mean',
                                                                       'Longitude': 'mean',
                                                                       'Confirmed': 'sum',
                                                                       'Deaths': 'sum',
                                                                       'Recovered': 'sum',
                                                                       'Active': 'sum'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    df = df[['date', 'Country/Region', 'Latitude', 'Longitude', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'share_of_last_week', 'percentage']]

    # Manually change some country centroids which are mislocated due to far off colonies
    df.loc[df['Country/Region'] == 'US', 'Latitude'] = 39.810489
    df.loc[df['Country/Region'] == 'US', 'Longitude'] = -98.555759

    df.loc[df['Country/Region'] == 'France', 'Latitude'] = 46.2276
    df.loc[df['Country/Region'] == 'France', 'Longitude'] = 2.2137

    df.loc[df['Country/Region'] == 'United Kingdom', 'Latitude'] = 55.3781
    df.loc[df['Country/Region'] == 'United Kingdom', 'Longitude'] = -3.4360

    df.loc[df['Country/Region'] == 'Denmark', 'Latitude'] = 56.2639
    df.loc[df['Country/Region'] == 'Denmark', 'Longitude'] = 9.5018

    df.loc[df['Country/Region'] == 'Netherlands', 'Latitude'] = 52.1326
    df.loc[df['Country/Region'] == 'Netherlands', 'Longitude'] = 5.2913

    df.loc[df['Country/Region'] == 'Canada', 'Latitude'] = 56.1304
    df.loc[df['Country/Region'] == 'Canada', 'Longitude'] = -106.346800

    return df

def us(data):
    print('processing US')
    df = data[data['Country/Region'] == 'US']
    df = df.groupby(['date', 'Province/State'], as_index=False).agg({'Confirmed': 'sum',
                                                                     'Deaths': 'sum',
                                                                     'Recovered': 'sum',
                                                                     'Active': 'sum'})
    df = df.merge(pd.read_csv('data/geo_us.csv'), left_on='Province/State', right_on='Province/State', how='left')
    df = df.rename(columns={'Province/State': 'Country/Region'})
    df = df[['date',
            'Country/Region',
            'Latitude',
            'Longitude',
            'Confirmed',
            'Active',
            'Deaths',
            'Recovered']].sort_values(['date', 'Country/Region'])
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    df = df[['date', 'Country/Region', 'Latitude', 'Longitude', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'share_of_last_week', 'percentage']]
    return df

def eu(data):
    print('processing Europe')
    eu = ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium',
      'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus',
      'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France',
      'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
      'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
      'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands',
      'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Romania',
      'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
      'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom',
      'Vatican City']
    df = data[data['Country/Region'].isin(eu)]
    df = df.groupby(['date', 'Country/Region'], as_index=False).agg({'Latitude': 'mean',
                                                                     'Longitude': 'mean',
                                                                     'Confirmed': 'sum',
                                                                     'Deaths': 'sum',
                                                                     'Recovered': 'sum',
                                                                     'Active': 'sum'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    df = df[['date', 'Country/Region', 'Latitude', 'Longitude', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'share_of_last_week', 'percentage']]

    # Manually change some country centroids which are mislocated due to far off colonies
    df.loc[df['Country/Region'] == 'US', 'Latitude'] = 39.810489
    df.loc[df['Country/Region'] == 'US', 'Longitude'] = -98.555759

    df.loc[df['Country/Region'] == 'France', 'Latitude'] = 46.2276
    df.loc[df['Country/Region'] == 'France', 'Longitude'] = 2.2137

    df.loc[df['Country/Region'] == 'United Kingdom', 'Latitude'] = 55.3781
    df.loc[df['Country/Region'] == 'United Kingdom', 'Longitude'] = -3.4360

    df.loc[df['Country/Region'] == 'Denmark', 'Latitude'] = 56.2639
    df.loc[df['Country/Region'] == 'Denmark', 'Longitude'] = 9.5018

    df.loc[df['Country/Region'] == 'Netherlands', 'Latitude'] = 52.1326
    df.loc[df['Country/Region'] == 'Netherlands', 'Longitude'] = 5.2913

    df.loc[df['Country/Region'] == 'Canada', 'Latitude'] = 59.050000
    df.loc[df['Country/Region'] == 'Canada', 'Longitude'] = -112.833333
    
    return df

def china(data):
    print('processing China')
    df = data[data['Country/Region'] == 'China']
    df = df.drop(['Country/Region', 'Admin2'], axis=1)
    df = df.rename(columns={'Province/State': 'Country/Region'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    df = df[['date', 'Country/Region', 'Latitude', 'Longitude', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'share_of_last_week', 'percentage']]
    return df

def us_county(data):
    print('processing US counties')
    df = data[data['Country/Region'] == 'US']
    df = df.assign(key=df['Admin2'] + ' County, ' + df['Province/State'])
    df = df.drop('Country/Region', axis=1)
    df = df.rename(columns={'key': 'Country/Region'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    df = df[['date', 'Country/Region', 'Latitude', 'Longitude', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'share_of_last_week', 'percentage']]
    return df

def global_population():
    # source: United Nations, https://population.un.org/wpp/Download/Standard/CSV/
    # 2019 data
    print()
    print('loading population')
    pop_global = pd.read_csv('data/WPP2019_TotalPopulationBySex.csv')
    pop_global = pop_global[(pop_global['Variant'] == 'Medium') & (pop_global['Time'] == 2020)][['Location', 'PopTotal']].reset_index(drop=True)
    pop_global['population'] = (pop_global['PopTotal'] * 1000).astype(int)
    pop_global['region'] = pop_global['Location']
    pop_global = pop_global[['region', 'population']]
    return pop_global

def us_population():
    # source: US Census, https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html
    # 2019 data projected from 2010 Census
    pop_us = pd.read_csv('data/nst-est2019-alldata.csv')
    pop_us = pop_us[['NAME', 'POPESTIMATE2019']]
    pop_us['region'] = pop_us['NAME']
    pop_us['population'] = pop_us['POPESTIMATE2019']
    pop_us = pop_us[['region', 'population']]
    return pop_us

def china_population(pop_global):
    # source: National Bureau of Statistics of China, http://data.stats.gov.cn/english/easyquery.htm?cn=E0103
    # Hong Kong source: World Bank, https://data.worldbank.org/indicator/SP.POP.TOTL?locations=HK
    # 2018 data
    pop_china = pd.read_csv('data/AnnualbyProvince.csv', header=3, encoding='ISO-8859-1')
    pop_china = pop_china[['Region', '2018']].iloc[:31]
    pop_china['region'] = pop_china['Region']
    pop_china['population'] = (pop_china['2018'] * 10000).astype(int)
    pop_china = pop_china[['region', 'population']]
    pop_china.loc[31] = ['Hong Kong', pop_global[pop_global['region'] == 'China, Hong Kong SAR']['population'].values[0]]
    pop_china.loc[32] = ['Macau', pop_global[pop_global['region'] == 'China, Macao SAR']['population'].values[0]]
    return pop_china

def population_to_worldwide(df, pop_global):
    df = pd.merge(df, pop_global, left_on='Country/Region', right_on='region', how='left').drop(columns='region')

    # correct mismatched country names
    df.loc[df['Country/Region'] == 'Bolivia', ['population']] = pop_global.loc[pop_global['region'] == 'Bolivia (Plurinational State of)']['population'].values
    df.loc[df['Country/Region'] == 'Brunei', ['population']] = pop_global.loc[pop_global['region'] == 'Brunei Darussalam']['population'].values
    df.loc[df['Country/Region'] == 'Burma', ['population']] = pop_global.loc[pop_global['region'] == 'Myanmar']['population'].values
    df.loc[df['Country/Region'] == 'Congo (Brazzaville)', ['population']] = pop_global.loc[pop_global['region'] == 'Congo']['population'].values
    df.loc[df['Country/Region'] == 'Congo (Kinshasa)', ['population']] = pop_global.loc[pop_global['region'] == 'Democratic Republic of the Congo']['population'].values
    df.loc[df['Country/Region'] == "Cote d'Ivoire", ['population']] = pop_global.loc[pop_global['region'] == "Côte d'Ivoire"]['population'].values
    df.loc[df['Country/Region'] == 'Iran', ['population']] = pop_global.loc[pop_global['region'] == 'Iran (Islamic Republic of)']['population'].values
    df.loc[df['Country/Region'] == 'Kosovo', ['population']] = 1845000  # source: https://data.worldbank.org/country/kosovo
    df.loc[df['Country/Region'] == 'South Korea', ['population']] = pop_global.loc[pop_global['region'] == 'Republic of Korea']['population'].values
    df.loc[df['Country/Region'] == 'Laos', ['population']] = pop_global.loc[pop_global['region'] == "Lao People's Democratic Republic"]['population'].values
    df.loc[df['Country/Region'] == 'Moldova', ['population']] = pop_global.loc[pop_global['region'] == 'Republic of Moldova']['population'].values
    df.loc[df['Country/Region'] == 'Russia', ['population']] = pop_global.loc[pop_global['region'] == 'Russian Federation']['population'].values
    df.loc[df['Country/Region'] == 'Taiwan', ['population']] = pop_global.loc[pop_global['region'] == 'China, Taiwan Province of China']['population'].values
    df.loc[df['Country/Region'] == 'Tanzania', ['population']] = pop_global.loc[pop_global['region'] == 'United Republic of Tanzania']['population'].values
    df.loc[df['Country/Region'] == 'Venezuela', ['population']] = pop_global.loc[pop_global['region'] == 'Venezuela (Bolivarian Republic of)']['population'].values
    df.loc[df['Country/Region'] == 'Vietnam', ['population']] = pop_global.loc[pop_global['region'] == 'Viet Nam']['population'].values
    df.loc[df['Country/Region'] == 'Syria', ['population']] = pop_global.loc[pop_global['region'] == 'Syrian Arab Republic']['population'].values
    df.loc[(df['Country/Region'] == 'US'), ['population']] = pop_global.loc[pop_global['region'] == 'United States of America']['population'].values

    df['population'] = df['population'] / 100000

    return df

def population_to_us(df, pop_us):
    df = pd.merge(df, pop_us, left_on='Country/Region', right_on='region', how='left').drop('region', axis=1)
    df.loc[df['Country/Region'] == 'Recovered', ['population']] = pop_us[pop_us['region'] == 'United States']['population'].values[0]
    df['population'] = df['population'] / 100000
    return df

def population_to_eu(df, pop_global):
    df = pd.merge(df, pop_global, left_on='Country/Region', right_on='region', how='left').drop('region', axis=1)
    df.loc[df['Country/Region'] == 'Kosovo', ['population']] = 1845000  # source: https://data.worldbank.org/country/kosovo
    df.loc[df['Country/Region'] == 'Moldova', ['population']] = pop_global.loc[pop_global['region'] == 'Republic of Moldova']['population'].values
    df['population'] = df['population'] / 100000
    return df

def population_to_china(df, pop_china):
    df = pd.merge(df, pop_china, left_on='Country/Region', right_on='region', how='left').drop('region', axis=1)
    df['population'] = df['population'] / 100000
    return df

def main(update):
    data = etl('time_series', 'web', update)
    if isinstance(data, str):
        return
    data.to_csv('data/dashboard_data.csv', index=False)

    pop_global = global_population()
    pop_us = us_population()
    pop_china = china_population(pop_global)

    df_worldwide = worldwide(data)
    df_worldwide = population_to_worldwide(df_worldwide, pop_global)
    df_worldwide.to_csv('data/df_worldwide.csv', index=False)

    df_us = us(data)
    df_us = population_to_us(df_us, pop_us)
    df_us.to_csv('data/df_us.csv', index=False)

    df_eu = eu(data)
    df_eu = population_to_eu(df_eu, pop_global)
    df_eu.to_csv('data/df_eu.csv', index=False)

    df_china = china(data)
    df_china = population_to_china(df_china, pop_china)
    df_china.to_csv('data/df_china.csv', index=False)

    df_us_county = us_county(data)
    df_us_county.to_csv('data/df_us_county.csv', index=False)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(update=str(sys.argv[1]))
    else:
        main(update='manual')