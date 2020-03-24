import pandas as pd
import numpy as np
import glob
import re
from datetime import date, timedelta
import io
import requests
import json


def etl(source='web'):
    if source=='folder':
        # Load files from folder
        path = 'data'
        all_files = glob.glob(path + "/*.csv")

        files = []

        for filename in all_files:
            file = re.search(r'([0-9]{2}\-[0-9]{2}\-[0-9]{4})', filename)[0]
            print(file)
            df = pd.read_csv(filename, index_col=None, header=0)
            df['date'] = pd.to_datetime(file)
            files.append(df)

    elif source=='web':
        # Load files from web
        file_date = date(2020, 1, 22)
        dates = []

        while file_date <= date.today():
            dates.append(file_date)
            file_date += timedelta(days=1)
            
        files = []
        for file in dates:
            file = file.strftime("%m-%d-%Y")
            print(file)
            url = r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(file)
            raw_string = requests.get(url).content
            df = pd.read_csv(io.StringIO(raw_string.decode('utf-8')))
            if b'404: Not Found\n' not in raw_string:
                df.to_csv('data/{}.csv'.format(file), index=False)
            df['date'] = pd.to_datetime(file)
            df.rename(columns={'Province_State': 'Province/State',
                               'Country_Region': 'Country/Region',
                               'Lat': 'Latitude',
                               'Long_': 'Longitude'}, inplace=True)
            files.append(df)

    df = pd.concat(files, axis=0, ignore_index=True, sort=False)

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
    df['Country/Region'].replace('Republic of Korea', 'North Korea', inplace=True)
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

    # South Korea data on March 10 seems to be mislabled as North Korea
    df.loc[(df['Country/Region'] == 'North Korea') & (df['date'] == '03-10-2020'), 'Country/Region'] = 'South Korea'

    # Re-order the columns for readability
    df = df[['date',
            'Country/Region',
            'Province/State',
            'Confirmed',
            'Deaths',
            'Recovered',
            'Latitude',
            'Longitude']]

    # Fill missing values as 0; create Active cases column
    df['Confirmed'] = df['Confirmed'].fillna(0).astype(int)
    df['Deaths'] = df['Deaths'].fillna(0).astype(int)
    df['Recovered'] = df['Recovered'].fillna(0).astype(int)
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']

    # Replace missing values for latitude and longitude
    df['Latitude'] = df['Latitude'].fillna(df.groupby('Province/State')['Latitude'].transform('mean'))
    df['Longitude'] = df['Longitude'].fillna(df.groupby('Province/State')['Longitude'].transform('mean'))
    return df

def views(df, states, eu):
    df_us = df[df['Province/State'].isin(states)]
    df_eu = df[df['Country/Region'].isin(eu)]
    df_eu = df_eu.append(pd.DataFrame({'date': [pd.to_datetime('2020-01-22'), pd.to_datetime('2020-01-23')],
                          'Country/Region': ['France', 'France'],
                          'Province/State': [np.nan, np.nan],
                          'Confirmed': [0, 0],
                          'Deaths': [0, 0],
                          'Recovered': [0, 0],
                          'Latitude': [np.nan, np.nan],
                          'Longitude': [np.nan, np.nan],
                          'Active': [0, 0]})).sort_index()

    df_us.drop('Country/Region', axis=1, inplace=True)
    df_us.rename(columns={'Province/State': 'Country/Region'}, inplace=True)

    return df_us, df_eu

def indicators(df, column):
    value = df[df['date'] == df['date'].iloc[-1]][column].sum()
    delta = df[df['date'] == df['date'].unique()[-2]][column].sum()

    return value, delta

def infections(data):
    df = pd.DataFrame()
    df['x'] = data.groupby('date')['date'].first()
    df['Confirmed'] = data.groupby('date')['Confirmed'].sum()
    df['Active'] = data.groupby('date')['Active'].sum()
    df['Recovered'] = data.groupby('date')['Recovered'].sum()
    df['Deaths'] = data.groupby('date')['Deaths'].sum()
    return df

def active_countries(data, regions):
    df = pd.DataFrame()
    for region in regions:
        df['x_{}'.format(region)] = data[data['Country/Region'] == region].groupby('date')['date'].first()
        df['y_{}'.format(region)] = data[data['Country/Region'] == region].groupby('date')['Active'].sum()
    return df

def stacked(data, regions, scope):
    df = pd.DataFrame()
    for region in regions:
        if data[(data['date'] == data['date'].iloc[-1]) & (data['Country/Region'] == region)]['Confirmed'].sum() > scope:
            df['x_{}'.format(region)] = data[data['Country/Region'] == region].groupby('date')['date'].first()
            for column in ['Confirmed', 'Active', 'Recovered', 'Deaths']:
                df['y_{}_{}'.format(region, column)] = data[data['Country/Region'] == region].groupby('date')[column].sum()
    return df

def map_data(data):
    df_world_map = pd.DataFrame()

    for date_index in range(len(df['date'].unique())):
        date = df['date'].unique()[date_index]

        df_world_map = data[data['date'] == date].groupby('Country/Region').agg({'Active': 'sum',
                                                                                'Longitude': 'mean',
                                                                                'Latitude': 'mean',
                                                                                'Country/Region': 'first'})
        # Manually change some country centroids which are mislocated due to far off colonies
        df_world_map.loc[df_world_map['Country/Region'] == 'US', 'Latitude'] = 39.810489
        df_world_map.loc[df_world_map['Country/Region'] == 'US', 'Longitude'] = -98.555759

        df_world_map.loc[df_world_map['Country/Region'] == 'France', 'Latitude'] = 46.2276
        df_world_map.loc[df_world_map['Country/Region'] == 'France', 'Longitude'] = -3.4360

        df_world_map.loc[df_world_map['Country/Region'] == 'United Kingdom', 'Latitude'] = 55.3781
        df_world_map.loc[df_world_map['Country/Region'] == 'United Kingdom', 'Longitude'] = 2.2137

        df_world_map.loc[df_world_map['Country/Region'] == 'Denmark', 'Latitude'] = 56.2639
        df_world_map.loc[df_world_map['Country/Region'] == 'Denmark', 'Longitude'] = 9.5018

        df_world_map.loc[df_world_map['Country/Region'] == 'Netherlands', 'Latitude'] = 52.1326
        df_world_map.loc[df_world_map['Country/Region'] == 'Netherlands', 'Longitude'] = 5.2913
    
    return df_world_map

if __name__ == '__main__':
    df = etl()
    df.to_csv('dashboard_data.csv', index=False)

    # available_countries = sorted(df['Country/Region'].unique())

    # states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
    #     'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida',
    #     'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
    #     'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
    #     'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
    #     'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
    #     'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    #     'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

    # eu = ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
    #     'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France',
    #     'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein',
    #     'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway',
    #     'Poland', 'Portugal', 'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
    #     'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom', 'Vatican City']

    # df_us, df_eu = views(df, states, eu)

    # value_ww_confirmed, delta_ww_confirmed = indicators(df, 'Confirmed')
    # value_ww_active, delta_ww_active = indicators(df, 'Active')
    # value_ww_recovered, delta_ww_recovered = indicators(df, 'Recovered')
    # value_ww_deaths, delta_ww_deaths = indicators(df, 'Deaths')

    # df_worldwide_infections = infections(df)
    # df_us_infections = infections(df_us)
    # df_eu_infections = infections(df_eu)

    # df_ww_active = active_countries(df, available_countries)
    # df_us_active = active_countries(df_us, states)
    # df_eu_active = active_countries(df_eu, eu)

    # df_ww_stacked = stacked(df, available_countries, 1000)
    # df_us_stacked = stacked(df_us, states, 20)
    # df_eu_stacked = stacked(df_eu, states, 1000)

    # df_world_map_ww = 
