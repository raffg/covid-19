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

available_countries = sorted(df['Country/Region'].unique())

available_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
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

def confirmed():
    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    text = '''
        # {:,}
        CUMULATIVE CONFIRMED
    '''.format(value)
    return text

def active():
    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    text = '''
        # {:,}
        CURRENTLY ACTIVE
    '''.format(value)
    return text

def recovered():
    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    text = '''
        # {:,}
        RECOVERED CASES
    '''.format(value)
    return text

def deaths():
    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    text = '''
        # {:,}
        DEATHS TO DATE
    '''.format(value)
    return text

def worldwide_trend():
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
                title="Worldwide Infections",
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

@app.callback(
    Output('active_countries', 'figure'),
    [Input('country_select', 'value')])
def active_countries(countries):
    traces = []
    for country in countries:
        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == country].groupby('date')['date'].first(),
                    y=df[df['Country/Region'] == country].groupby('date')['Active'].sum(),
                    name=country))
    return {
            'data': traces,
            'layout': go.Layout(
                    title="Active Cases by Country",
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
    [Input('column_select', 'value')])
def stacked_active(column):
    traces = []
    for region in df['Country/Region'].unique():
        if df[(df['date'] == df['date'].iloc[-1]) & (df['Country/Region'] == region)]['Confirmed'].sum() > 1000:
            traces.append(go.Scatter(
                x=df[df['Country/Region'] == region].groupby('date')['date'].first(),
                y=df[df['Country/Region'] == region].groupby('date')[column].sum(),
                name=region,
                hoverinfo='x+y+z+text+name',
                stackgroup='one'))
    return {
            'data': traces,
            'layout': go.Layout(
                title="{} Cases Worldwide (Countries with greater than 1000 confirmed cases)".format(column),
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
    [Input('date_slider', 'value')])
def world_map_active(date_index):
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

    html.Div(dcc.RadioItems(
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

    html.Div(dcc.Markdown(confirmed(), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'left',
        'display': 'inline-block'})
    ),

    html.Div(dcc.Markdown(active(), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'left',
        'display': 'inline-block'})
    ),

    html.Div(dcc.Markdown(deaths(), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'right',
        'display': 'inline-block'})
    ),

    html.Div(dcc.Markdown(recovered(), style={
        'textAlign': 'center',
        'color': colors['red'],
        'width': '25%',
        'float': 'right',
        'display': 'inline-block'})
    ),

    html.Div([
        html.Div(
            worldwide_trend(),
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
                options=[{'label': i, 'value': i} for i in available_countries],
                value=['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany'],
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
    app.run_server(debug=True)
