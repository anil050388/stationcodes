import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.H1(children='Home page', style={
             'fontSize': 50, 'textAlign': 'center'}),

    html.Div(children='''
About:
This is a small Application(still in development stage) by using Plotly Muli pages and  integration it with databases PostgreSQL and MongoDB. For Map visualization we have used Plotly and Dash Leaflet Heroku
''', style={'background':'black','color':'white'}),
html.Br(),
    html.Div(children='''
Station Search:
Search tool of Indian Railway Station Codes help you know more about the railway stations. The codes generally help in booking train tickets. Here, you can find the codes of all Indian railway stations. You only need to put the name of the city or station or click the state in the search tool and it will give you the right code of the station.
''',style={'background':'black','color':'white'}),
html.Br(),
    html.Div(children='''
Train Schedule Search:
Train Schedule Search tool rovides a simple interface to check the train schedule of Indian Railways and IRCTC trains. All you need to do is to fill in the train number in the form above. 
    ''',style={'background':'black','color':'white'}),
])
