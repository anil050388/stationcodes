from dash.dependencies import Input, Output
from dash import Dash, html, Input, Output, ctx, dcc, dash_table, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from numerize import numerize
import json
import dash
from dash import clientside_callback

dash.register_page(__name__)

# Read GeoJson and Excel files for the station list across the states
df = pd.read_excel("stationlist.xlsx")
with open('states_india.geojson') as file:
    file_data = json.load(file)
state_id_map = {}
for feature in file_data['features']:
    feature['id'] = feature['properties']['state_code']
    state_id_map[feature['properties']['st_nm']] = feature['id']
df['id'] = df['State'].apply(lambda x: state_id_map[x])

# Column for the states
States = list(df['State'].unique())
States.insert(0, 'All States')

layout = html.Div([
    html.H1("Station Code of Indian Railways Stations "),
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(id='map', config={'displayModeBar': 'hover',
                                                'scrollZoom': False},
                              style={'background': '#00FC87', 'padding-bottom': '0px', 'padding-left': '0px'})
                ]),
            ], className="twelve columns map"),
        ]),
        dbc.Row([
            dcc.Dropdown(id='Selected_value',
                         placeholder='Please Click the State (On Map) Or Select All...',
                         # type='text',
                         value='All States',
                         options=[
                                     {"label": x, "value": x}
                                     for x in States
                         ],
                         clearable=False,
                         searchable=False,
                         style={'margin': '10px',
                                'background': 'black',
                                'color': 'white',
                                'font-weight': 'bold',
                                'width': '100%'}
                         )

        ]),
        dbc.Row([
            dbc.Label("Show number of rows", id="rowstable"),
            dcc.Dropdown(
                id="row_drop",
                multi=False,
                options=[10, 25, 50, 100],
                value=10, clearable=False, style={'width': '35%'}),

            my_table := dash_table.DataTable(

                columns=[
                    {'name': 'Station Code', 'id': 'Station Code', 'type': 'text'},
                    {'name': 'Station Name', 'id': 'Station Name', 'type': 'text'},
                    {'name': 'State', 'id': 'State', 'type': 'text'},
                ],

                style_cell={'textAlign': 'left',
                            'font-family': 'sans-serif'
                            },
                filter_action="native",
                page_size=10,
                style_data={
                    'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'font-family': 'tahoma',
                    'font-size': '13px',
                    'direction': 'rtl',
                    'position': 'relative',
                    'border': '1px solid blue'
                },
                style_header={'font-weight': 'Bold',
                              'border': '1px solid pink'}
            ),
        ])

    ])
])


@callback(Output('map', 'figure'),
          Input('Selected_value', 'value'))
def updatecard(Selected_value):
    States_list = df.groupby(['id', 'State'])[
        'State'].count().reset_index(name='counts')

    fig = px.choropleth(
        States_list,
        geojson=file_data,
        color="counts",
        locations="id", hover_name="State",
        hover_data=["State"])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0)),
    #   width=1350,
    #   height=400)
    # fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'))
    return fig


@callback([Output(my_table, 'data'),
           Output(my_table, 'page_size')],
          Input('Selected_value', 'value'),
          Input('row_drop', 'value'))
def updatecard(Selected_value, row_drop):
    df1 = df.copy()
    if Selected_value == "All States":
        All_codes = df1[['code', 'name', 'State']]
    else:
        All_codes = df1[df1['State'] ==
                        Selected_value][['code', 'name', 'State']]
    All_codes.columns = ['Station Code', 'Station Name', 'State']
    All_codes = All_codes.sort_values(by=['Station Code'])
    return All_codes.to_dict('records'), row_drop


@callback(Output('Selected_value', 'value'),
          [Input('map', 'clickData')])
def updatecard(clickData):
    if clickData is not None:
        StateName = df[df['id'] == clickData['points']
                       [0]['location']]['State'].unique()
        return ''.join(StateName)
    else:
        value = ''
        return "All States"