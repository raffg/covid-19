import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import glob
import re
from datetime import date, timedelta
import io
import requests

# Standard plotly imports
import plotly.graph_objects as go
from plotly.offline import iplot, init_notebook_mode
# Using plotly + cufflinks in offline mode
import cufflinks
cufflinks.go_offline(connected=True)
init_notebook_mode(connected=True)


app = dash.Dash()
app.config.suppress_callback_exceptions=True

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
            df['date'] = pd.to_datetime(file)
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

data = etl(source='folder')
df = data

colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333',
    'red': '#BF0000'
}

available_countries = sorted(df['Country/Region'].unique())

states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
    'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida',
    'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
    'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
    'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
    'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
    'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

eu = ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
    'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France',
    'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein',
    'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway',
    'Poland', 'Portugal', 'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
    'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom', 'Vatican City']

region_options = {'Worldwide': available_countries, 'United States': states, 'Europe': eu}

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
df = data

df_us.drop('Country/Region', axis=1, inplace=True)
df_us.rename(columns={'Province/State': 'Country/Region'}, inplace=True)

@app.callback(
    Output('confirmed_ind', 'figure'),
    [Input('global_format', 'value')])
def confirmed(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Confirmed'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': '.2%',
                              'relative': True,
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "CUMULATIVE CONFIRMED"},
                font=dict(color=colors['red']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height=200
                )
            }

@app.callback(
    Output('active_ind', 'figure'),
    [Input('global_format', 'value')])
def active(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Active'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': '.2%',
                              'relative': True,
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "CURRENTLY ACTIVE"},
                font=dict(color=colors['red']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height=200
                )
            }

@app.callback(
    Output('recovered_ind', 'figure'),
    [Input('global_format', 'value')])
def recovered(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Recovered'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': '.2%',
                              'relative': True,
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "RECOVERED CASES"},
                font=dict(color=colors['red']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height=200
                )
            }

@app.callback(
    Output('deaths_ind', 'figure'),
    [Input('global_format', 'value')])
def deaths(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Deaths'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': '.2%',
                              'relative': True,
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "DEATHS TO DATE"},
                font=dict(color=colors['red']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height=200
                )
            }

@app.callback(
    Output('worldwide_trend', 'figure'),
    [Input('global_format', 'value')])
def worldwide_trend(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    traces = [go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Confirmed'].sum(),
                    name="Total Confirmed",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Active'].sum(),
                    name="Active Cases",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Recovered'].sum(),
                    name="Recovered",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Deaths'].sum(),
                    name="Deaths",
                    mode='lines')]
    return {
            'data': traces,
            'layout': go.Layout(
                title="{} Infections".format(view),
                xaxis_title="Date",
                yaxis_title="Number of Individuals",
                font=dict(color=colors['text']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                xaxis=dict(gridcolor=colors['grid']),
                yaxis=dict(gridcolor=colors['grid'])
                )
            }

@app.callback(
    Output('country_select', 'options'),
    [Input('global_format', 'value')])
def set_active_options(selected_view):
    return [{'label': i, 'value': i} for i in region_options[selected_view]]

@app.callback(
    Output('country_select', 'value'),
    [Input('global_format', 'value'),
     Input('country_select', 'options')])
def set_countries_value(view, available_options):
    if view == 'Worldwide':
        return ['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany']
    elif view == 'United States':
        return ['California', 'Colorado', 'Florida', 'New York', 'Washington']
    elif view == 'Europe':
        return ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom']
    else:
        return ['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany']

@app.callback(
    Output('active_countries', 'figure'),
    [Input('global_format', 'value'),
     Input('country_select', 'value')])
def active_countries(view, countries):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    traces = []
    for country in countries:
        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == country].groupby('date')['date'].first(),
                    y=df[df['Country/Region'] == country].groupby('date')['Active'].sum(),
                    name=country,
                    mode='lines'))
    return {
            'data': traces,
            'layout': go.Layout(
                    title="Active Cases by Region",
                    xaxis_title="Date",
                    yaxis_title="Number of Individuals",
                    font=dict(color=colors['text']),
                    paper_bgcolor=colors['background'],
                    plot_bgcolor=colors['background'],
                    xaxis=dict(gridcolor=colors['grid']),
                    yaxis=dict(gridcolor=colors['grid']),
                    hovermode='closest'
                )
            }

@app.callback(
    Output('stacked_active', 'figure'),
    [Input('global_format', 'value'),
     Input('column_select', 'value')])
def stacked_active(view, column):
    if view == 'Worldwide':
        df = data
        scope = 1000
    elif view == 'United States':
        df = df_us
        scope = 20
    elif view == 'Europe':
        df = df_eu
        scope = 1000
    else:
        df = data
        scope = 1000

    traces = []
    for region in df['Country/Region'].unique():
        if df[(df['date'] == df['date'].iloc[-1]) & (df['Country/Region'] == region)]['Confirmed'].sum() > scope:
            traces.append(go.Scatter(
                x=df[df['Country/Region'] == region].groupby('date')['date'].first(),
                y=df[df['Country/Region'] == region].groupby('date')[column].sum(),
                name=region,
                hoverinfo='x+y+z+text+name',
                stackgroup='one'))
    return {
            'data': traces,
            'layout': go.Layout(
                title="{} {} Cases (Regions with greater than {} confirmed cases)".format(view, column, scope),
                # annotations=[dict(x=1,
                #                 y=1,
                #                 text = 'Regions with greater than {} confirmed cases'.format(scope),
                #                 showarrow=False,
                #                 xanchor='center')],
                xaxis_title="Date",
                yaxis_title="Number of Individuals",
                font=dict(color=colors['text']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                xaxis=dict(gridcolor=colors['grid']),
                yaxis=dict(gridcolor=colors['grid']),
                hovermode='closest'
            )
        }

def world_map_confirmed():
    # World map
    df_world_map = df[df['date'] == df['date'].iloc[-1]].groupby('Country/Region').agg({'Confirmed': 'sum',
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

    return dcc.Graph(
        id='world_map_confirmed',
        figure={
            'data': [
                go.Scattergeo(
                    lon = df_world_map['Longitude'],
                    lat = df_world_map['Latitude'],
                    text = df_world_map['Country/Region'] + ': ' + df_world_map['Confirmed'].astype(str) + ' cases',
                    mode = 'markers',
                    marker_size = np.sqrt(df_world_map['Confirmed'] / 5),
            #         marker_size = 100 * df_world_map['Confirmed'] / df_world_map['Confirmed'].max(),
                    marker = dict(reversescale = False,
                                autocolorscale = False,
                                symbol = 'circle',
                                line = dict(width=1, color='rgba(102, 102, 102)'),
                                colorscale = 'Reds',
                                cmin = 0,
                                color = df_world_map['Confirmed'],
                                cmax = df_world_map['Confirmed'].max(),
                                colorbar_title="Confirmed Cases"),
                    fillcolor=colors['background'])
            ],
            'layout': go.Layout(
                title = 'Number of cumulative confirmed cases by country',
                geo=dict(scope='world',
                        projection_type="natural earth",
                        showland = True,
                        landcolor = "rgb(100, 125, 100)",
                        showocean = True,
                        oceancolor = "rgb(150, 150, 250)",
                        showcountries=True,
                        showlakes=False),
                font=dict(color=colors['text']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background']
            )
        }
    )

@app.callback(
    Output('world_map_active', 'figure'),
    [Input('global_format', 'value'),
     Input('date_slider', 'value')])
def world_map_active(view, date_index):
    if view == 'Worldwide':
        df = data
        scope='world'
        projection_type='natural earth'
    elif view == 'United States':
        df = df_us
        scope='usa'
        projection_type='albers usa'
    elif view == 'Europe':
        df = df_eu
        scope='europe'
        projection_type='natural earth'
    else:
        df = data
        scope='world'
        projection_type='natural earth',

    # World map
    date = df['date'].unique()[date_index]
    # date = df['date'].iloc[-1]
    df_world_map = df[df['date'] == date].groupby('Country/Region').agg({'Active': 'sum',
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

    return {
            'data': [
                go.Scattergeo(
                    lon = df_world_map['Longitude'],
                    lat = df_world_map['Latitude'],
                    text = df_world_map['Country/Region'] + ': ' + df_world_map['Active'].astype(str) + ' cases',
                    mode = 'markers',
                    marker_size = np.sqrt(df_world_map['Active'] / 5),
            #         marker_size = 100 * df_world_map['Active'] / df_world_map['Active'].max(),
                    marker = dict(reversescale = False,
                                autocolorscale = False,
                                symbol = 'circle',
                                line = dict(width=1, color='rgba(102, 102, 102)'),
                                colorscale = 'Reds',
                                cmin = 0,
                                color = df_world_map['Active'],
                                cmax = df_world_map['Active'].max(),
                                colorbar_title="Active Cases")
                    )
            ],
            'layout': go.Layout(
                title ='Active Cases by Geography',
                geo=dict(scope=scope,
                        projection_type=projection_type,
                        showland = True,
                        landcolor = "rgb(100, 125, 100)",
                        showocean = True,
                        oceancolor = "rgb(150, 150, 250)",
                        showcountries=True,
                        showlakes=False),
                font=dict(color=colors['text']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background']
            )
        }


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='COVID-19',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
        ),

    html.Div(children='Select focus for the dashboard', style={
        'textAlign': 'center',
        'color': colors['text']
        }),

    html.Div(
        dcc.RadioItems(
            id='global_format',
            options=[{'label': i, 'value': i} for i in ['Worldwide', 'United States', 'Europe']],
            value='Worldwide',
            labelStyle={'float': 'center', 'display': 'inline-block'}
            ), style={'textAlign': 'center',
                'color': colors['text'],
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'
            }
        ),

    html.Div(
        dcc.Graph(id='confirmed_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div(
        dcc.Graph(id='active_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div(
        dcc.Graph(id='deaths_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div(
        dcc.Graph(id='recovered_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div([
        html.Div(
            dcc.Graph(id='worldwide_trend'),
            style={'width': '50%', 'float': 'left', 'display': 'inline-block'}
            ),

        html.Div([
            dcc.Graph(id='stacked_active'),
            html.Div(dcc.RadioItems(
                        id='column_select',
                        options=[{'label': i, 'value': i} for i in ['Confirmed', 'Active', 'Recovered', 'Deaths']],
                        value='Active',
                        labelStyle={'float': 'center', 'display': 'inline-block'},
                        style={'textAlign': 'center',
                            'color': colors['text'],
                            'width': '100%',
                            'float': 'center',
                            'display': 'inline-block'
                            }),
                    style={'width': '100%', 'float': 'center', 'display': 'inline-block'})
            ],
            style={'width': '50%', 'float': 'right', 'vertical-align': 'bottom'}
        )],
        style={'width': '98%', 'float': 'center', 'vertical-align': 'bottom'}
        ),

    html.Div([
        dcc.Graph(id='world_map_active'),
        dcc.Slider(
            id='date_slider',
            min=list(range(len(df['date'].unique())))[0],
            max=list(range(len(df['date'].unique())))[-1],
            value=list(range(len(df['date'].unique())))[-1],
            marks={(idx): (date if idx%10==0 else '') for idx, date in enumerate(sorted(set([item.strftime("%m-%d-%Y") for item in df['date']])))},
            step=None)],
        style={'width': '50%', 'display': 'inline-block'}
        ),

    html.Div([
            dcc.Graph(id='active_countries'),
            dcc.Dropdown(
                id='country_select',
                multi=True,
                style={'width': '95%', 'float': 'center'}
                )
            ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),

    html.Div(
        dcc.Markdown('''
            Built by [Greg Rafferty](https://www.linkedin.com/in/gregrafferty/)  
            Source data: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)
            '''),
            style={
                'textAlign': 'center',
                'color': '#FEFEFE',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'}
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=False)
