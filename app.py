import dash
import dash_core_components as dcc
import dash_html_components as html

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

def etl(source='web'):
    if source=='folder':
        # Load files from folder
        path = 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports'
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

df = etl(source='folder')

colors = {
    'background': '#111111',
    'text': '#BEBEBE', #'#7FDBFF',
    'grid': '#333333',
    'red': '#BF0000'
}

available_countries = df['Country/Region'].unique()
available_states = df['Province/State'].unique()

def confirmed(df):
    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    text = '''
        # {:,}
        CONFIRMED
    '''.format(value)
    return text

def active(df):
    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    text = '''
        # {:,}
        ACTIVE
    '''.format(value)
    return text

def recovered(df):
    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    text = '''
        # {:,}
        RECOVERED
    '''.format(value)
    return text

def deaths(df):
    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    text = '''
        # {:,}
        DEATHS
    '''.format(value)
    return text

def worldwide_trend(df):
    traces = [go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Confirmed'].sum(),
                    name="Total Confirmed"),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Active'].sum(),
                    name="Active Cases"),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Recovered'].sum(),
                    name="Recovered"),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Deaths'].sum(),
                    name="Deaths")]
    return dcc.Graph(
        id='worldwide_trend',
        figure={
            'data': traces,
            'layout': go.Layout(
                    title="COVID-19 infections Worldwide",
                    xaxis_title="Date",
                    yaxis_title="Number of Individuals",
                    font=dict(color=colors['text']),
                    paper_bgcolor=colors['background'],
                    plot_bgcolor=colors['background'],
                    xaxis=dict(gridcolor=colors['grid']),
                    yaxis=dict(gridcolor=colors['grid'])
                    )
            }
        )

def active_countries(df, countries=['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany']):
    traces = []
    for country in countries:
        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == country].groupby('date')['date'].first(),
                    y=df[df['Country/Region'] == country].groupby('date')['Active'].sum(),
                    name=country))
    return dcc.Graph(
        id='active_countries',
        figure={
            'data': traces,
            'layout': go.Layout(
                    title="Active COVID-19 cases",
                    xaxis_title="Date",
                    yaxis_title="Number of Individuals",
                    font=dict(color=colors['text']),
                    paper_bgcolor=colors['background'],
                    plot_bgcolor=colors['background'],
                    xaxis=dict(gridcolor=colors['grid']),
                    yaxis=dict(gridcolor=colors['grid'])
                )
            }
        )

def world_map_confirmed(df):
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

def world_map_active(df):
    # World map
    df_world_map = df[df['date'] == df['date'].iloc[-1]].groupby('Country/Region').agg({'Active': 'sum',
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
        id='world_map_active',
        figure={
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
                title ='Number of active cases by country',
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


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='COVID-19',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='A basic dashboard for tracking the pandemic', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div(dcc.Markdown(confirmed(df), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'left',
        'display': 'inline-block'})
    ),

    html.Div(dcc.Markdown(active(df), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'left',
        'display': 'inline-block'})
    ),

    html.Div(dcc.Markdown(deaths(df), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'right',
        'display': 'inline-block'})
    ),

    html.Div(dcc.Markdown(recovered(df), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'right',
        'display': 'inline-block'})
    ),

    html.Div(
        worldwide_trend(df),
        style={'width': '50%', 'float': 'left', 'display': 'inline-block'}
    ),

    html.Div(
        active_countries(df),
        style={'width': '50%', 'float': 'right', 'display': 'inline-block'}
    ),

    html.Div(
        world_map_active(df),
        style={'width': '50%', 'display': 'inline-block'}
        ),
    html.Div(
        world_map_confirmed(df),
        style={'width': '50%', 'float': 'right', 'display': 'inline-block'}
        )
])

if __name__ == '__main__':
    app.run_server(debug=True)
