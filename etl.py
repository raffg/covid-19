import pandas as pd
import numpy as np
import glob
import re
from datetime import date, timedelta
import io
import requests


def save_from_web(url):
    url = r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/{}'.format(url)
    raw_string = requests.get(url).content
    return pd.read_csv(io.StringIO(raw_string.decode('utf-8')))

def load_time_series(source='web'):
    if source == 'web':
        prepend = r'csse_covid_19_time_series/time_series_covid19_'

        print('confirmed_us')
        confirmed_us = save_from_web(r'{}confirmed_US.csv'.format(prepend))
        confirmed_us.to_csv('data/raw/time_series_covid19_confirmed_US.csv', index=False)

        print('confirmed_global')
        confirmed_global = save_from_web(r'{}confirmed_global.csv'.format(prepend))
        confirmed_global.to_csv('data/raw/time_series_covid19_confirmed_global.csv', index=False)

        print('deaths_us')
        deaths_us = save_from_web(r'{}deaths_US.csv'.format(prepend))
        deaths_us.to_csv('data/raw/time_series_covid19_deaths_us.csv', index=False)

        print('deaths_global')
        deaths_global = save_from_web(r'{}deaths_global.csv'.format(prepend))
        deaths_global.to_csv('data/raw/time_series_covid19_deaths_global.csv', index=False)

        print('recovered_global')
        recovered_global =save_from_web(r'{}recovered_global.csv'.format(prepend))
        recovered_global.to_csv('data/raw/time_series_covid19_recovered_global.csv', index=False)

    elif source == 'folder':
        confirmed_us = pd.read_csv('data/raw/time_series_covid19_confirmed_US')
        confirmed_global = pd.read_csv('data/raw/time_series_covid19_confirmed_global')
        deaths_us = pd.read_csv('data/raw/time_series_covid19_deaths_us')
        deaths_global = pd.read_csv('data/raw/time_series_covid19_deaths_global')
        recovered_global = pd.read_csv('data/raw/time_series_covid19_recovered_global')

    dates = []
    for column in confirmed_global.columns:
        if re.search(r'([0-9]{1,2}\/[0-9]{1,2}\/(20))', column):
            dates.append(column)

    # Melt (de-pivot), join, and union the above tables
    df = pd.concat([
            pd.merge(
                pd.melt(confirmed_us,
                    id_vars=['Country_Region', 'Province_State', 'Admin2', 'Lat', 'Long_'],
                    value_vars=dates).rename(columns={'Country_Region': 'Country/Region',
                                                    'Province_State': 'Province/State',
                                                    'Lat': 'Latitude',
                                                    'Long_': 'Longitude',
                                                    'variable': 'date',
                                                    'value': 'Confirmed'}),
                pd.melt(deaths_us,
                    id_vars=['Country_Region', 'Province_State', 'Admin2', 'Lat', 'Long_'],
                    value_vars=dates).rename(columns={'Country_Region': 'Country/Region',
                                                    'Province_State': 'Province/State',
                                                    'Lat': 'Latitude',
                                                    'Long_': 'Longitude',
                                                    'variable': 'date',
                                                    'value': 'Deaths'}),
                on=['date',
                    'Country/Region',
                    'Province/State',
                    'Admin2',
                    'Latitude',
                    'Longitude']).assign(Recovered=np.nan)[['date',
                                                            'Country/Region',
                                                            'Province/State',
                                                            'Admin2',
                                                            'Latitude',
                                                            'Longitude',
                                                            'Confirmed',
                                                            'Deaths',
                                                            'Recovered']],
            pd.merge(
                pd.merge(
                    pd.melt(confirmed_global,
                        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
                        value_vars=dates).rename(columns={'Lat': 'Latitude',
                                                        'Long': 'Longitude',
                                                        'variable': 'date',
                                                        'value': 'Confirmed'}).assign(Admin2=np.nan),
                    pd.melt(deaths_global,
                        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
                        value_vars=dates).rename(columns={'Lat': 'Latitude',
                                                        'Long': 'Longitude',
                                                        'variable': 'date',
                                                        'value': 'Deaths'}).assign(Admin2=np.nan),
                    on=['date', 'Country/Region', 'Province/State', 'Admin2', 'Latitude', 'Longitude']),
                pd.melt(recovered_global,
                        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
                        value_vars=dates).rename(columns={'Lat': 'Latitude',
                                                        'Long': 'Longitude',
                                                        'variable': 'date',
                                                        'value': 'Recovered'}).assign(Admin2=np.nan),
                on=['date', 'Country/Region', 'Province/State', 'Admin2', 'Latitude', 'Longitude']
            )[['date',
            'Country/Region',
            'Province/State',
            'Admin2',
            'Latitude',
            'Longitude',
            'Confirmed',
            'Deaths',
            'Recovered']]
        ])

    df['date'] = pd.to_datetime(df['date'])

    # State "Recovered" state for unassigned recoveries
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
            df = save_from_web(url)
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

def etl(layout='time_series', source='web'):
    if layout == 'time_series':
        df = load_time_series(source=source)
    elif layout == 'daily_reports':
        df = load_daily_reports(source=source)

    # create Active cases column
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']

    # Re-order the columns for readability
    df = df[['date',
            'Country/Region',
            'Province/State',
            'Admin2',
            'Confirmed',
            'Active',
            'Deaths',
            'Recovered',
            'Latitude',
            'Longitude']]

    return df

def worldwide(data):
    df = data.groupby(['date', 'Country/Region'], as_index=False).agg({'Confirmed': 'sum',
                                                                                 'Deaths': 'sum',
                                                                                 'Recovered': 'sum',
                                                                                 'Active': 'sum'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    return df

def us(data):
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
    return df

def eu(data):
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
    df = df.groupby(['date', 'Country/Region'], as_index=False).agg({'Latitude': 'first',
                                                                    'Longitude': 'first',
                                                                    'Confirmed': 'sum',
                                                                    'Deaths': 'sum',
                                                                    'Recovered': 'sum',
                                                                    'Active': 'sum'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))

    return df

def china(data):
    df = data[data['Country/Region'] == 'China']
    df = df.drop(['Country/Region', 'Admin2'], axis=1)
    df = df.rename(columns={'Province/State': 'Country/Region'})
    df['share_of_last_week'] = 100 * (df['Confirmed'] - df.groupby('Country/Region')['Confirmed'].shift(7, fill_value=0)) / df['Confirmed']
    df['share_of_last_week'] = df['share_of_last_week'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df.loc[df['share_of_last_week'] < 0, 'share_of_last_week'] = 0
    df['percentage'] = df['share_of_last_week'].apply(lambda x: '{:.1f}'.format(x))
    return df

def us_county(data):
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

if __name__ == '__main__':
    data = etl('time_series', 'web')
    data.to_csv('data/dashboard_data.csv', index=False)

    df_worldwide = worldwide(data)
    df_worldwide.to_csv('data/df_worldwide.csv', index=False)

    df_us = us(data)
    df_us.to_csv('data/df_us.csv', index=False)

    df_eu = eu(data)
    df_eu.to_csv('data/df_eu.csv', index=False)

    df_china = china(data)
    df_china.to_csv('data/df_china.csv', index=False)

    df_us_county = us_county(data)
    df_us_county.to_csv('data/df_us_county.csv', index=False)
