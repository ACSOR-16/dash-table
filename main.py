# !pip install dash
# !pip install dash-renderer
# !pip install dash_html_components
# !pip install dash_core_components
# # import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

app.layout = html.Div([
    html.Label(children="Analisis Sismico Dinamico", title="Analisis Sismico Dinamico"),
    
    html.Label(children="Capacidad Portante", title="Capacidad Portante", id="cap_por"),
    dcc.Input(id="cap_por", type="number"),
    
    html.Label(children="Factor de Uso", title="Factor de Uso", id="fac_uso"),
    dcc.Input(id="fac_uso", type="number"),

    html.Label(children="Factor de Zona", title="Factor de Zona", id="fac_zon"),
    dcc.Input(id="fac_zon", type="number"),
    
    html.Label(children="Factor de suelo", title="Factor de suelo", id="fac_sue"),
    dcc.Input(id="fac_sue", type="number"),
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)
