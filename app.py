import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import plotly
import plotly.graph_objects as go


app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True
app.title = 'COVID-19'

dash_colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333',
    'red': '#BF0000',
    'blue': '#466fc2',
    'green': '#5bc246'
}

df_worldwide = pd.read_csv('data/df_worldwide.csv')
df_worldwide['percentage'] = df_worldwide['percentage'].astype(str)
df_worldwide['date'] = pd.to_datetime(df_worldwide['date'])

# selects the "data last updated" date
update = df_worldwide['date'].dt.strftime('%B %d, %Y').iloc[-1]

available_countries = sorted(df_worldwide['Country/Region'].unique())

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

df_us = pd.read_csv('data/df_us.csv')
df_us['percentage'] = df_us['percentage'].astype(str)
df_us['date'] = pd.to_datetime(df_us['date'])

df_eu = pd.read_csv('data/df_eu.csv')
df_eu['percentage'] = df_eu['percentage'].astype(str)
df_eu['date'] = pd.to_datetime(df_eu['date'])

df_china = pd.read_csv('data/df_china.csv')
df_china['percentage'] = df_china['percentage'].astype(str)
df_china['date'] = pd.to_datetime(df_china['date'])

df_us_counties = pd.read_csv('data/df_us_county.csv')
df_us_counties['percentage'] = df_us_counties['percentage'].astype(str)
df_us_counties['Country/Region'] = df_us_counties['Country/Region'].astype(str)
df_us_counties['date'] = pd.to_datetime(df_us_counties['date'])

@app.callback(
    Output('confirmed_ind', 'figure'),
    [Input('global_format', 'value')])
def confirmed(view):
    '''
    creates the CUMULATIVE CONFIRMED indicator
    '''
    if view == 'Worldwide':
        df = df_worldwide
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = df_worldwide

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
    '''
    creates the CURRENTLY ACTIVE indicator
    '''
    if view == 'Worldwide':
        df = df_worldwide
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = df_worldwide

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
    '''
    creates the RECOVERED CASES indicator
    '''
    if view == 'Worldwide':
        df = df_worldwide
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = df_worldwide

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
    '''
    creates the DEATHS TO DATE indicator
    '''
    if view == 'Worldwide':
        df = df_worldwide
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = df_worldwide

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
    [Input('global_format', 'value'),
     Input('population_select', 'value')])
def worldwide_trend(view, population):
    '''
    creates the upper-left chart (aggregated stats for the view)
    '''
    if view == 'Worldwide':
        df = df_worldwide
    elif view == 'United States':
        df = df_us
        df_us.loc[df_us['Country/Region'] == 'Recovered', ['population']] = 0
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = df_worldwide

    if population == 'absolute':
        confirmed = df.groupby('date')['Confirmed'].sum()
        active = df.groupby('date')['Active'].sum()
        recovered = df.groupby('date')['Recovered'].sum()
        deaths = df.groupby('date')['Deaths'].sum()
        title_suffix = ''
        hover = '%{y:,g}'
    elif population == 'percent':
        df = df.dropna(subset=['population'])
        confirmed = df.groupby('date')['Confirmed'].sum() / df.groupby('date')['population'].sum()
        active = df.groupby('date')['Active'].sum() / df.groupby('date')['population'].sum()
        recovered = df.groupby('date')['Recovered'].sum() / df.groupby('date')['population'].sum()
        deaths = df.groupby('date')['Deaths'].sum() / df.groupby('date')['population'].sum()
        title_suffix = ' per 100,000 people'
        hover = '%{y:,.2f}'
    else:
        confirmed = df.groupby('date')['Confirmed'].sum()
        active = df.groupby('date')['Active'].sum()
        recovered = df.groupby('date')['Recovered'].sum()
        deaths = df.groupby('date')['Deaths'].sum()
        title_suffix = ''
        hover = '%{y:,g}'

    traces = [go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=confirmed,
                    hovertemplate=hover,
                    name="Confirmed",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=active,
                    hovertemplate=hover,
                    name="Active",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=recovered,
                    hovertemplate=hover,
                    name="Recovered",
                    mode='lines'),
                go.Scatter(
                    x=df.groupby('date')['date'].first(),
                    y=deaths,
                    hovertemplate=hover,
                    name="Deaths",
                    mode='lines')]
    return {
            'data': traces,
            'layout': go.Layout(
                title="{} Infections{}".format(view, title_suffix),
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
    '''
    sets allowable options for regions in the upper-right chart drop-down
    '''
    return [{'label': i, 'value': i} for i in region_options[selected_view]]

@app.callback(
    Output('country_select', 'value'),
    [Input('global_format', 'value'),
     Input('country_select', 'options')])
def set_countries_value(view, available_options):
    '''
    sets default selections for regions in the upper-right chart drop-down
    '''
    if view == 'Worldwide':
        return ['US', 'Italy', 'United Kingdom', 'Spain', 'France', 'Russia', 'Brazil', 'Sweden', 'Belgium', 'Peru', 'India']
    elif view == 'United States':
        return ['New York', 'New Jersey', 'California', 'Texas', 'Florida', 'Georgia', 'Arizona', 'North Carolina', 'Colorado']
    elif view == 'Europe':
        return ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom', 'Belgium', 'Sweden']
    elif view == 'China':
        return ['Hubei', 'Guangdong', 'Xinjiang', 'Zhejiang', 'Hunan', 'Hong Kong', 'Macau']
    else:
        return ['US', 'Italy', 'United Kingdom', 'Spain', 'France', 'Germany', 'Russia']

@app.callback(
    Output('active_countries', 'figure'),
    [Input('global_format', 'value'),
     Input('country_select', 'value'),
     Input('column_select', 'value'),
     Input('population_select', 'value')])
def active_countries(view, countries, column, population):
    '''
    creates the upper-right chart (sub-region analysis)
    '''
    if view == 'Worldwide':
        df = df_worldwide
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    elif view == 'China':
        df = df_china
    else:
        df = df_worldwide

    if population == 'absolute':
        column_label = column
        hover = '%{y:,g}<br>%{x}'
    elif population == 'percent':
        column_label = '{} per 100,000'.format(column)
        df = df.dropna(subset=['population'])
        hover = '%{y:,.2f}<br>%{x}'
    else:
        column_label = column
        hover = '%{y:,g}<br>%{x}'

    traces = []
    countries = df[(df['Country/Region'].isin(countries)) &
                   (df['date'] == df['date'].max())].groupby('Country/Region')['Confirmed'].sum().sort_values(ascending=False).index.to_list()
    for country in countries:
        if population == 'absolute':
            y_data = df[df['Country/Region'] == country].groupby('date')[column].sum()
            recovered = df[df['Country/Region'] == 'Recovered'].groupby('date')[column].sum()
        elif population == 'percent':
            y_data = df[df['Country/Region'] == country].groupby('date')[column].sum() / df[df['Country/Region'] == country].groupby('date')['population'].first()
            recovered = df[df['Country/Region'] == 'Recovered'].groupby('date')[column].sum() / df[df['Country/Region'] == country].groupby('date')['population'].first()
        else:
            y_data = df[df['Country/Region'] == country].groupby('date')[column].sum()
            recovered = df[df['Country/Region'] == 'Recovered'].groupby('date')[column].sum()

        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == country].groupby('date')['date'].first(),
                    y=y_data,
                    hovertemplate=hover,
                    name=country,
                    mode='lines'))
    if column == 'Recovered':
        traces.append(go.Scatter(
                    x=df[df['Country/Region'] == 'Recovered'].groupby('date')['date'].first(),
                    y=recovered,
                    hovertemplate=hover,
                    name='Unidentified',
                    mode='lines'))
    return {
            'data': traces,
            'layout': go.Layout(
                    title="{} by Region".format(column_label),
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
    '''
    creates the lower-left chart (map)
    '''
    if view == 'Worldwide':
        df = df_worldwide
        scope = 'world'
        projection_type = 'natural earth'
        sizeref = 35
    elif view == 'United States':
        scope = 'usa'
        projection_type = 'albers usa'
        df = df_us_counties
        sizeref = 7
    elif view == 'Europe':
        df = df_eu
        scope = 'europe'
        projection_type = 'natural earth'
        sizeref = 15
    elif view == 'China':
        df = df_china
        scope = 'asia'
        projection_type = 'natural earth'
        sizeref = 3
    else:
        df = df_worldwide
        scope = 'world'
        projection_type = 'natural earth',
        sizeref = 10
    df = df[(df['date'] == df['date'].unique()[date_index]) & (df['Confirmed'] > 0)]
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

def hex_to_rgba(h, alpha=1):
    '''
    converts color value in hex format to rgba format with alpha transparency
    '''
    return tuple([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [alpha])

@app.callback(
    Output('trajectory', 'figure'),
    [Input('global_format', 'value'),
     Input('date_slider', 'value')])
def trajectory(view, date_index):
    '''
    creates the lower-right chart (trajectory)
    '''
    if view == 'Worldwide':
        df = df_worldwide
        scope = 'countries'
        threshold = 50000
    elif view == 'United States':
        df = df_us
        scope = 'states'
        threshold = 10000
    elif view == 'Europe':
        df = df_eu
        scope = 'countries'
        threshold = 10000
    elif view == 'China':
        df = df_china
        scope = 'provinces'
        threshold = 1000
    else:
        df = df_worldwide
        scope = 'countries'
        threshold = 50000

    date = df_worldwide['date'].unique()[date_index]

    df = df.groupby(['date', 'Country/Region'], as_index=False)['Confirmed'].sum()
    df['previous_week'] = df.groupby(['Country/Region'])['Confirmed'].shift(7, fill_value=0)
    df['new_cases'] = df['Confirmed'] - df['previous_week']
    df['new_cases'] = df['new_cases'].clip(lower=0)

    xmax = np.log(1.25 * df['Confirmed'].max()) / np.log(10)
    xmin = np.log(threshold) / np.log(10)
    ymax = np.log(1.25 * df['new_cases'].max()) / np.log(10)
    ymin = np.log(10)

    countries_full = df.groupby(by='Country/Region', as_index=False)['Confirmed'].max().sort_values(by='Confirmed', ascending=False)['Country/Region'].to_list()
    
    df = df[df['date'] <= date]

    countries = df.groupby(by='Country/Region', as_index=False)['Confirmed'].max().sort_values(by='Confirmed', ascending=False)
    countries = countries[countries['Confirmed'] > threshold]['Country/Region'].to_list()
    countries = [country for country in countries_full if country in countries]

    traces = []
    trace_colors = plotly.colors.qualitative.D3
    color_idx = 0

    for country in countries:
        filtered_df = df[df['Country/Region'] == country].reset_index()
        idx = filtered_df['Confirmed'].sub(threshold).gt(0).idxmax()
        trace_data = filtered_df[idx:].copy()
        trace_data['date'] = pd.to_datetime(trace_data['date'])
        trace_data['date'] = trace_data['date'].dt.strftime('%b %d, %Y')

        marker_size = [0] * (len(trace_data) - 1) + [10]
        color = trace_colors[color_idx % len(trace_colors)]
        marker_color = 'rgba' + str(hex_to_rgba(color, 1))
        line_color = 'rgba' + str(hex_to_rgba(color, .5))

        traces.append(
            go.Scatter(
                    x=trace_data['Confirmed'],
                    y=trace_data['new_cases'],
                    mode='lines+markers',
                    marker=dict(color=marker_color,
                                size=marker_size,
                                line=dict(width=0)),
                    line=dict(color=line_color, width=2),
                    name=country,
                    text = ['{}, {}: {:,} confirmed; {:,} from previous week'.format(country,
                                                                                trace_data['date'].iloc[i],
                                                                                trace_data['Confirmed'].iloc[i],
                                                                                trace_data['new_cases'].iloc[i]) \
                                                                                    for i in range(len(trace_data))],
                    hoverinfo='text')
        )

        color_idx += 1

    return {
        'data': traces,
        'layout': go.Layout(
                title='Trajectory of Cases<br>({} with greater than {:,} confirmed cases)'.format(scope, threshold),
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

    html.Div(children='Data last updated {} end-of-day'.format(update), style={
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

    html.Div(dcc.Markdown('Display data in the below two charts as total values or as values relative to population:'),
        style={
            'textAlign': 'center',
            'color': dash_colors['text'],
            'width': '100%',
            'float': 'center',
            'display': 'inline-block'}),

    html.Div(dcc.RadioItems(id='population_select',
            options=[{'label': 'Total values', 'value': 'absolute'},
                        {'label': 'Values per 100,000 of population', 'value': 'percent'}],
            value='absolute',
            labelStyle={'float': 'center', 'display': 'inline-block'},
            style={'textAlign': 'center',
                'color': dash_colors['text'],
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'
                })
        ),

    html.Div(  # worldwide_trend and active_countries
        [
            html.Div(
                dcc.Graph(id='worldwide_trend'),
                style={'width': '50%', 'float': 'left', 'display': 'inline-block'}
                ),
            html.Div([
                dcc.Graph(id='active_countries'),
                html.Div([
                    dcc.RadioItems(
                        id='column_select',
                        options=[{'label': i, 'value': i} for i in ['Confirmed', 'Active', 'Recovered', 'Deaths']],
                        value='Confirmed',
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

    html.Div(dcc.Markdown(' '),
        style={
            'textAlign': 'center',
            'color': dash_colors['text'],
            'width': '100%',
            'float': 'center',
            'display': 'inline-block'}),

    html.Div(dcc.Graph(id='world_map'),
        style={'width': '50%',
            'display': 'inline-block'}
        ),

    html.Div([dcc.Graph(id='trajectory')],
        style={'width': '50%',
            'float': 'right',
            'display': 'inline-block'}),

    html.Div(html.Div(dcc.Slider(id='date_slider',
                min=list(range(len(df_worldwide['date'].unique())))[0],
                max=list(range(len(df_worldwide['date'].unique())))[-1],
                value=list(range(len(df_worldwide['date'].unique())))[-1],
                marks={(idx): {'label': date.format(u"\u2011", u"\u2011") if
                    (idx-4)%7==0 else '', 'style':{'transform': 'rotate(30deg) translate(0px, 7px)'}} for idx, date in
                    enumerate(sorted(set([item.strftime("%m{}%d{}%Y") for
                    item in df_worldwide['date']])))},  # for weekly marks,
                # marks={(idx): (date.format(u"\u2011", u"\u2011") if
                #     date[4:6] in ['01', '15'] else '') for idx, date in
                #     enumerate(sorted(set([item.strftime("%m{}%d{}%Y") for
                #     item in df_worldwide['date']])))},  # for bi-monthly makrs
                step=1,
                vertical=False,
                updatemode='mouseup'),
            style={'width': '94.74%', 'float': 'left'}),  # width = 1 - (100 - x) / x
        style={'width': '95%', 'float': 'right'}),  # width = x
    
    html.Div(dcc.Markdown('''
            &nbsp;  
            &nbsp;  
            Built by [Greg Rafferty](https://www.linkedin.com/in/gregrafferty/)  
            Source data: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)  
            Instructions and feature documention [here](https://github.com/raffg/covid-19/blob/master/README.md)  
            '''),
            style={
                'textAlign': 'center',
                'color': dash_colors['text'],
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'}
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=False)
