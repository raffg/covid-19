import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import plotly.graph_objects as go


app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions=True
app.title = 'COVID-19'

data = pd.read_csv('dashboard_data.csv')
data['date'] = pd.to_datetime(data['date'])
update = data['date'].dt.strftime('%B %d, %Y').iloc[-1]

geo_us = pd.read_csv('geo_us.csv')

dash_colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333',
    'red': '#BF0000',
    'blue': '#466fc2',
    'green': '#5bc246'
}

available_countries = sorted(data['Country/Region'].unique())

states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
          'Colorado', 'Connecticut', 'Delaware', 'District of Columbia',
          'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
          'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
          'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
          'New Jersey', 'New Mexico', 'New York', 'North Carolina',
          'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee',
          'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
          'West Virginia', 'Wisconsin', 'Wyoming']

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

china = ['Anhui', 'Beijing', 'Chongqing', 'Fujian', 'Gansu', 'Guangdong',
         'Guangxi', 'Guizhou', 'Hainan', 'Hebei', 'Heilongjiang', 'Henan',
         'Hong Kong', 'Hubei', 'Hunan', 'Inner Mongolia', 'Jiangsu',
         'Jiangxi', 'Jilin', 'Liaoning', 'Macau', 'Ningxia', 'Qinghai',
         'Shaanxi', 'Shandong', 'Shanghai', 'Shanxi', 'Sichuan', 'Tianjin',
         'Tibet', 'Xinjiang', 'Yunnan', 'Zhejiang']

region_options = {'Worldwide': available_countries,
                  'United States': states,
                  'Europe': eu,
                  'China': china}

df_us = pd.read_csv('df_us.csv')
df_eu = pd.read_csv('df_eu.csv')
df_china = pd.read_csv('df_china.csv')
df_us_counties = pd.read_csv('df_us_county.csv')
df_us_counties['percentage'] = df_us_counties['percentage'].astype(str)
df_us_counties['key'] = df_us_counties['key'].astype(str)

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
    elif view == 'China':
        df = df_china
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Confirmed'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': ',g',
                              'relative': False,
                              'increasing': {'color': dash_colors['blue']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "CUMULATIVE CONFIRMED"},
                font=dict(color=dash_colors['red']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background'],
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
    elif view == 'China':
        df = df_china
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Active'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': ',g',
                              'relative': False,
                              'increasing': {'color': dash_colors['blue']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "CURRENTLY ACTIVE"},
                font=dict(color=dash_colors['red']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background'],
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
    elif view == 'China':
        df = df_china
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Recovered'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': ',g',
                              'relative': False,
                              'increasing': {'color': dash_colors['blue']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "RECOVERED CASES"},
                font=dict(color=dash_colors['red']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background'],
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
    elif view == 'China':
        df = df_china
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Deaths'].sum()
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': delta,
                              'valueformat': ',g',
                              'relative': False,
                              'increasing': {'color': dash_colors['blue']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "DEATHS TO DATE"},
                font=dict(color=dash_colors['red']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background'],
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
    elif view == 'China':
        df = df_china
    else:
        df = data

    traces = [go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Confirmed'].sum(),
                    name="Confirmed",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=df.groupby('date')['Active'].sum(),
                    name="Active",
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
                yaxis_title="Number of Cases",
                font=dict(color=dash_colors['text']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background'],
                xaxis=dict(gridcolor=dash_colors['grid']),
                yaxis=dict(gridcolor=dash_colors['grid'])
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
        return ['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany', 'Iran']
    elif view == 'United States':
        return ['New York', 'New Jersey', 'Massachusetts', 'Pennsylvania', 'California', 'Florida', 'Michigan', 'Louisiana', 'Washington']
    elif view == 'Europe':
        return ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom']
    elif view == 'China':
        return ['Hubei', 'Guangdong', 'Henan', 'Zhejiang', 'Hunan', 'Hong Kong', 'Anhui']
    else:
        return ['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany']

@app.callback(
    Output('active_countries', 'figure'),
    [Input('global_format', 'value'),
     Input('country_select', 'value'),
     Input('column_select', 'value')])
def active_countries(view, countries, column):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = data

    traces = []
    countries = df[(df['Country/Region'].isin(countries)) &
                   (df['date'] == df['date'].max())].groupby('Country/Region')['Active'].sum().sort_values(ascending=False).index.to_list()
    for country in countries:
        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == country].groupby('date')['date'].first(),
                    y=df[df['Country/Region'] == country].groupby('date')[column].sum(),
                    name=country,
                    mode='lines',
                    hoverinfo='x+y+name'))
    if column == 'Recovered':
        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == 'Recovered'].groupby('date')['date'].first(),
                    y=df[df['Country/Region'] == 'Recovered'].groupby('date')[column].sum(),
                    name='Unidentified',
                    mode='lines',
                    hoverinfo='x+y+name'))
    return {
            'data': traces,
            'layout': go.Layout(
                    title="{} by Region".format(column),
                    xaxis_title="Date",
                    yaxis_title="Number of Cases",
                    font=dict(color=dash_colors['text']),
                    paper_bgcolor=dash_colors['background'],
                    plot_bgcolor=dash_colors['background'],
                    xaxis=dict(gridcolor=dash_colors['grid']),
                    yaxis=dict(gridcolor=dash_colors['grid']),
                    hovermode='closest'
                )
            }

@app.callback(
    Output('world_map', 'figure'),
    [Input('global_format', 'value'),
     Input('date_slider', 'value')])
def world_map(view, date_index):
    if view == 'Worldwide':
        df = data
        df = world_map_processing(df, date_index)
        scope='world'
        projection_type='natural earth'
        sizeref=10
    elif view == 'United States':
        scope='usa'
        projection_type='albers usa'
        df = df_us_counties
        df = df[df['date'] == df['date'].unique()[date_index]]
        df = df.rename(columns={'key': 'Country/Region'})
        sizeref=3
    elif view == 'Europe':
        df = df_eu
        df = world_map_processing(df, date_index)
        scope='europe'
        projection_type='natural earth'
        sizeref=10
    elif view == 'China':
        df = df_china
        df = world_map_processing(df, date_index)
        scope='asia'
        projection_type='natural earth'
        sizeref=3
    else:
        df = data
        df = world_map_processing(df, date_index)
        scope='world'
        projection_type='natural earth',
        sizeref=10
    return {
            'data': [
                go.Scattergeo(
                    lon = df['Longitude'],
                    lat = df['Latitude'],
                    text = df['Country/Region'] + ': ' +\
                        ['{:,}'.format(i) for i in df['Confirmed']] +\
                        ' total cases, ' + df['percentage'] +\
                        '% from previous week',
                    hoverinfo = 'text',
                    mode = 'markers',
                    marker = dict(reversescale = False,
                        autocolorscale = False,
                        symbol = 'circle',
                        size = np.sqrt(df['Confirmed']),
                        sizeref = sizeref,
                        sizemin = 0,
                        line = dict(width=.5, color='rgba(0, 0, 0)'),
                        colorscale = 'Reds',
                        cmin = 0,
                        color = df['share_of_last_week'],
                        cmax = 100,
                        colorbar = dict(
                            title = "Percentage of<br>cases occurring in<br>the previous week",
                            thickness = 30)
                        )
                    )
            ],
            'layout': go.Layout(
                title ='Number of Cumulative Confirmed Cases (size of marker)<br>and Share of New Cases from the Previous Week (color)',
                geo=dict(scope=scope,
                        projection_type=projection_type,
                        showland = True,
                        landcolor = "rgb(100, 125, 100)",
                        showocean = True,
                        oceancolor = "rgb(80, 150, 250)",
                        showcountries=True,
                        showlakes=True),
                font=dict(color=dash_colors['text']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background']
            )
        }

def world_map_processing(df, date_index):
    # World map
    date = df['date'].unique()[date_index]

    df_world_map = df[df['date'] == date].groupby('Country/Region').agg({'Confirmed': 'sum',
                                                                        'Longitude': 'mean',
                                                                        'Latitude': 'mean',
                                                                        'Country/Region': 'first'})

    if date_index > 7:
        idx7 = date_index - 7
    else:
        idx7 = 0

    df_world_map['share_of_last_week'] = ((df[df['date'] == date].groupby('Country/Region')['Confirmed'].sum() -
                                df[df['date'] == df['date'].unique()[idx7]].groupby('Country/Region')['Confirmed'].sum()) /
                                df[df['date'] == date].groupby('Country/Region')['Confirmed'].sum()) * 100

    df_world_map['percentage'] = df_world_map['share_of_last_week'].fillna(0).apply(lambda x: '{:.1f}'.format(x))

    # Manually change some country centroids which are mislocated due to far off colonies
    df_world_map.loc[df_world_map['Country/Region'] == 'US', 'Latitude'] = 39.810489
    df_world_map.loc[df_world_map['Country/Region'] == 'US', 'Longitude'] = -98.555759

    df_world_map.loc[df_world_map['Country/Region'] == 'France', 'Latitude'] = 46.2276
    df_world_map.loc[df_world_map['Country/Region'] == 'France', 'Longitude'] = 2.2137

    df_world_map.loc[df_world_map['Country/Region'] == 'United Kingdom', 'Latitude'] = 55.3781
    df_world_map.loc[df_world_map['Country/Region'] == 'United Kingdom', 'Longitude'] = -3.4360

    df_world_map.loc[df_world_map['Country/Region'] == 'Denmark', 'Latitude'] = 56.2639
    df_world_map.loc[df_world_map['Country/Region'] == 'Denmark', 'Longitude'] = 9.5018

    df_world_map.loc[df_world_map['Country/Region'] == 'Netherlands', 'Latitude'] = 52.1326
    df_world_map.loc[df_world_map['Country/Region'] == 'Netherlands', 'Longitude'] = 5.2913

    df_world_map.loc[df_world_map['Country/Region'] == 'Canada', 'Latitude'] = 59.050000
    df_world_map.loc[df_world_map['Country/Region'] == 'Canada', 'Longitude'] = -112.833333

    df_world_map = df_world_map[df_world_map['Country/Region'] != 'Cruise Ship']
    df_world_map = df_world_map[df_world_map['Country/Region'] != 'Diamond Princess']

    return df_world_map

@app.callback(
    Output('trajectory', 'figure'),
    [Input('global_format', 'value'),
     Input('date_slider', 'value')])
def trajectory(view, date_index):
    if view == 'Worldwide':
        df = data
        scope = 'countries'
        threshold = 1000
    elif view == 'United States':
        df = data[data['Country/Region'] == 'US']
        df = df.drop('Country/Region', axis=1)
        df = df.rename(columns={'Province/State': 'Country/Region'})
        scope = 'states'
        threshold = 1000
    elif view == 'Europe':
        df = data[data['Country/Region'].isin(eu)]
        scope = 'countries'
        threshold = 1000
    elif view == 'China':
        df = data[data['Country/Region'] == 'China']
        df = df.drop('Country/Region', axis=1)
        df = df.rename(columns={'Province/State': 'Country/Region'})
        scope = 'provinces'
        threshold = 1000
    else:
        df = data
        scope = 'countries'
        threshold = 1000

    date = data['date'].unique()[date_index]

    df = df.groupby(['date', 'Country/Region'], as_index=False)['Confirmed'].sum()
    df['previous_week'] = df.groupby(['Country/Region'])['Confirmed'].shift(7, fill_value=0)
    df['new_cases'] = df['Confirmed'] - df['previous_week']
    df['new_cases'] = df['new_cases'].clip(lower=0)

    xmax = np.log(1.25 * df['Confirmed'].max()) / np.log(10)
    xmin = np.log(threshold) / np.log(10)
    ymax = np.log(1.25 * df['new_cases'].max()) / np.log(10)
    if df[df['Confirmed'] >= threshold]['new_cases'].min() == 0:
        ymin = 0
    else:
        ymin = np.log(.8 * df[df['Confirmed'] >= threshold]['new_cases'].min()) / np.log(10)

    countries_full = df.groupby(by='Country/Region', as_index=False)['Confirmed'].max().sort_values(by='Confirmed', ascending=False)['Country/Region'].to_list()
    
    df = df[df['date'] <= date]

    countries = df.groupby(by='Country/Region', as_index=False)['Confirmed'].max().sort_values(by='Confirmed', ascending=False)
    countries = countries[countries['Confirmed'] > threshold]['Country/Region'].to_list()
    countries = [country for country in countries_full if country in countries]

    traces = []

    for country in countries:
        filtered_df = df[df['Country/Region'] == country].reset_index()
        idx = filtered_df['Confirmed'].sub(threshold).gt(0).idxmax()
        trace_data = filtered_df[idx:].copy()
        trace_data['date'] = pd.to_datetime(trace_data['date'])
        trace_data['date'] = trace_data['date'].dt.strftime('%b %d, %Y')

        marker_size = [0] * (len(trace_data) - 1)
        marker_size.append(6)

        traces.append(
            go.Scatter(
                    x=trace_data['Confirmed'],
                    y=trace_data['new_cases'],
                    mode='lines+markers',
                    marker=dict(size=marker_size, line=dict(width=0)),
                    name=country,
                    text=trace_data['date'],
                    hoverinfo='x+text+name')
        )

    return {
        'data': traces,
        'layout': go.Layout(
                title='Trajectory of Cases<br>({} with greater than {} confirmed cases)'.format(scope, threshold),
                xaxis_type="log",
                yaxis_type="log",
                xaxis_title='Total Confirmed Cases',
                yaxis_title='New Confirmed Cases (in the past week)',
                font=dict(color=dash_colors['text']),
                paper_bgcolor=dash_colors['background'],
                plot_bgcolor=dash_colors['background'],
                xaxis=dict(gridcolor=dash_colors['grid'],
                           range=[xmin, xmax]),
                yaxis=dict(gridcolor=dash_colors['grid'],
                           range=[ymin, ymax]),
                hovermode='closest',
                showlegend=True
            )
        }

app.layout = html.Div(style={'backgroundColor': dash_colors['background']}, children=[
    html.H1(children='COVID-19',
        style={
            'textAlign': 'center',
            'color': dash_colors['text']
            }
        ),

    html.Div(children='Data last updated {} at 5pm Pacific time'.format(update), style={
        'textAlign': 'center',
        'color': dash_colors['text']
        }),
    
    html.Div(children='Select focus for the dashboard:', style={
        'textAlign': 'center',
        'color': dash_colors['text']
        }),

    html.Div(dcc.RadioItems(id='global_format',
            options=[{'label': i, 'value': i} for i in ['Worldwide', 'United States', 'Europe', 'China']],
            value='Worldwide',
            labelStyle={'float': 'center', 'display': 'inline-block'}
            ), style={'textAlign': 'center',
                'color': dash_colors['text'],
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'
            }
        ),

    html.Div(dcc.Graph(id='confirmed_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div(dcc.Graph(id='active_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div(dcc.Graph(id='deaths_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div(dcc.Graph(id='recovered_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
            }
        ),

    html.Div([html.Div(dcc.Graph(id='worldwide_trend'),
            style={'width': '50%', 'float': 'left', 'display': 'inline-block'}
            ),
        html.Div([
            dcc.Graph(id='active_countries'),
            html.Div([
                dcc.RadioItems(
                    id='column_select',
                    options=[{'label': i, 'value': i} for i in ['Confirmed', 'Active', 'Recovered', 'Deaths']],
                    value='Active',
                    labelStyle={'float': 'center', 'display': 'inline-block'},
                    style={'textAlign': 'center',
                        'color': dash_colors['text'],
                        'width': '100%',
                        'float': 'center',
                        'display': 'inline-block'
                        }),
                dcc.Dropdown(
                    id='country_select',
                    multi=True,
                    style={'width': '95%', 'float': 'center'}
                    )],
                style={'width': '100%', 'float': 'center', 'display': 'inline-block'})
            ],
            style={'width': '50%', 'float': 'right', 'vertical-align': 'bottom'}
        )],
        style={'width': '98%', 'float': 'center', 'vertical-align': 'bottom'}
        ),

    html.Div(dcc.Graph(id='world_map'),
        style={'width': '50%',
            'display': 'inline-block'}
        ),

    html.Div([dcc.Graph(id='trajectory')],
        style={'width': '50%',
            'float': 'right',
            'display': 'inline-block'}),

    html.Div(html.Div(dcc.Slider(id='date_slider',
                min=list(range(len(data['date'].unique())))[0],
                max=list(range(len(data['date'].unique())))[-1],
                value=list(range(len(data['date'].unique())))[-1],
                marks={(idx): (date.format(u"\u2011", u"\u2011") if
                    (idx-4)%7==0 else '') for idx, date in
                    enumerate(sorted(set([item.strftime("%m{}%d{}%Y") for
                    item in data['date']])))},
                step=1,
                vertical=False,
                updatemode='mouseup'),
            style={'width': '88.89%', 'float': 'left'}), # width = 1 - (100 - x) / x
        style={'width': '90%', 'float': 'right'}), # width = x

    html.Div(dcc.Markdown(' '),
        style={
            'textAlign': 'center',
            'color': '#FEFEFE',
            'width': '100%',
            'float': 'center',
            'display': 'inline-block'}),
    
    html.Div(dcc.Markdown('''
            Built by [Greg Rafferty](https://www.linkedin.com/in/gregrafferty/)  
            Source data: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)  
            Instructions and feature documention [here](https://github.com/raffg/covid-19/blob/master/README.md)  
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
