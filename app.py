import dash
from dash import html, dcc, Dash
import dash_bootstrap_components as dbc

metaTags = [
    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]

# Import style sheet CSS for Basic Dash App
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, meta_tags=metaTags, external_stylesheets=[
           dbc.themes.CYBORG, dbc.icons.BOOTSTRAP], use_pages=True)

app.layout = html.Div([
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}",
                     href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)
