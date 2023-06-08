import ast
import dash_leaflet.express as dlx
import dash_leaflet as dl
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import dash
from dash import Dash, html, Input, Output, ctx, dcc, dash_table, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from pymongo import MongoClient


dash.register_page(__name__)

# Making Connection
#MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
MONGODB_CONNECTION_STRING = os.environ.get('TOKEN')
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.metalprices
collections = db["Schedule"]

# Cool, dark tiles by Stadia Maps.
# url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
url = 'https://tile.openstreetmap.org/${z}/${x}/${y}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

df = px.data.tips()
df1 = pd.read_excel("trainslist.xlsx")
df2 = pd.read_excel("combined.xlsx")
trains = df1['number'].unique()
layout = html.Div(
    [
        html.H1("Train Schedule"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='Selected_value',
                             placeholder='Please Select Train Number...',
                             value=trains[0],
                             options=[
                                 {"label": x, "value": x}
                                 for x in trains
                             ],
                    clearable=False,
                    style={'margin': '10px',
                                 'background': 'black',
                                 'color': 'white',
                                 'font-weight': 'bold',
                                               'width': '100%'}
                )
            ], className="six columns"),
        ]),
        dbc.Row([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='train_name'),
                    html.Div(id='train_number'),
                    html.Div(id='duration'),
                    html.Div(id='Fstation_code'),
                    html.Div(id='Tstation_code')
                ])
            ])
        ]),
        html.Div(id="leaf_map"),
        dbc.Row([
            dbc.Label("Show number of rows", id="rowstable"),
            dcc.Dropdown(
                id="row_drop",
                multi=False,
                options=[10, 25, 50, 100],
                value=10, clearable=False, style={'width': '35%'}),

            my_table1 := dash_table.DataTable(

                columns=[
                    {'name': 'Arrival', 'id': 'arrival', 'type': 'text'},
                    {'name': 'Day', 'id': 'day', 'type': 'text'},
                    {'name': 'Station Name', 'id': 'station_name', 
                     'type': 'text'},
                    {'name': 'Station Code', 'id': 'station_code', 
                     'type': 'text'},
                    {'name': 'Train Number', 'id': 'train_number', 
                     'type': 'text'},
                    {'name': 'Departure', 'id': 'departure', 
                     'type': 'text'},
                ],

                style_cell={'textAlign': 'left',
                            'font-family': 'sans-serif'
                            },
                filter_action="native",
                page_size=10,
                style_data={
                    'overflow-x': 'auto',
                    'border-collapse': 'collapse',
                    'border-spacing': '0',
                    'font-family': 'tahoma',
                    'font-size': '13px',
                    'border': '1px solid #ddd'
                },
                style_header={'font-weight': 'Bold',
                              'overflow-x': 'auto',
                              'border-collapse': 'collapse',
                              'border-spacing': '0',
                              'border': '1px solid pink'}
            ),
        ])
    ]
)

@callback([Output('leaf_map', 'children'),
           Output(my_table1, 'data'),
           Output(my_table1, 'page_size'),
           Output('train_number', 'children'),
           Output('train_name', 'children'),
           Output('duration', 'children'),
           Output('Fstation_code', 'children'),
           Output('Tstation_code', 'children')],
           Input('Selected_value', 'value'),
           Input('row_drop', 'value'))
def updatecard(Selected_value, row_drop):
    if Selected_value:
        # Cool, dark tiles by Stadia Maps.
        url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
        attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

        trainnum = f'{Selected_value}'
        pl = df1[df1['number'] == trainnum][['name', 'number',
                                              'duration_h',
                                              'duration_m', 
                                              'from_station_code', 
                                              'to_station_code']]
        number = pl['number'].to_string(index=False)
        name = pl['name'].to_string(index=False)
        hours = pl['duration_h'].to_string(index=False)
        hours = "{:.0f}".format(float(hours))
        minutes = pl['duration_m'].to_string(index=False)
        minutes = "{:.0f}".format(float(minutes))
        froms = pl['from_station_code'].to_string(index=False)
        tos = pl['to_station_code'].to_string(index=False)
        name_id = html.H6("Train Name:   " + name.capitalize())
        number_id = html.P("Train Number:   " + number)
        duration = html.P("Duration: " + hours +
                        " hours " + minutes + " minutes ")
        fromst = html.P("From Station:   " + froms)
        tost = html.P("To Station:   " + tos)

        # Logic for Map
        places = df1[df1['number'] == trainnum]['locations'].tolist()
        places_convert = ast.literal_eval(places[0])

        latlong = []
        for places in places_convert:
            latlong.append([float(x) for x in places])

        list_places = []
        for place in latlong:
            dict_places = dict()
            dict_places['lon'] = place[0]
            center_lon = place[0]
            dict_places['lat'] = place[1]
            center_lat = place[1]
            compar = str([place[0], place[1]])
            sq = df2[df2['lastresort'] ==
                     compar]['address_x'].to_string(index=False)
            dict_places['popup'] = sq
            list_places.append(dict_places)
        data = dlx.dicts_to_geojson(list_places)
        patterns = [dict(offset='5%', repeat='10%', marker={})]
        polyline = dl.Polyline(positions=list_places)
        marker_pattern = dl.PolylineDecorator(
            children=polyline, patterns=patterns)
        tabit = pd.DataFrame()
        cursor = collections.find({'train_number': trainnum})
        for schedule in cursor:
            sched = schedule
            df_train = pd.DataFrame(sched, index=[0])
            tabit = pd.concat([tabit, df_train])
        All_codes = tabit[['arrival', 'day',
                           'station_name', 'station_code', 'train_number', 'departure']]
        fig = go.Figure()
        return dl.Map([
            dl.TileLayer(url=url, maxZoom=10, attribution=attribution),
            dl.GeoJSON(data=data)],
            # marker_pattern],
            center=(center_lat, center_lon), zoom=6, 
            style=
            {'width': '100%', 'height': '60vh', 'margin': "auto",
             "display":"block"}),All_codes.to_dict('records'),row_drop, number_id, name_id,duration, fromst, tost