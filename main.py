from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    
    html.Div([
            html.Div([

            html.Div([
                html.B("Análisis Sísmico Dinamico"),
                
                dash_table.DataTable(
                    id='Análisis-sismico-dinamico',
                    columns=[{
                        'name': i,
                        'id': i,
                        'deletable': False,
                        'renamable': False
                    } for i in ['Factores', 'Valores']],
                    data=[
                        {'Factores':"f'c Concreto", 'Valores':10},
                        {'Factores':'Factor de Uso', 'Valores':10},
                        {'Factores':'Factor de Zona', 'Valores':10},
                        {'Factores':'Factor de suelo', 'Valores':10},
                    ],
                    editable=True,
                    row_deletable=False,
                    # style={
                    #     "marginTop": "20px"
                    # },
                )
            ], style={
                "margin": "40px 0px 50px 50px"
            }),
            
            html.Div([
                html.B("Dimensiones de Terreno"),
                
                dash_table.DataTable(
                    id='dimensiones-terreno',
                    columns=[{
                        'name': i,
                        'id': i,
                        'deletable': False,
                        'renamable': False
                    } for i in ['Dimension', 'Valor']],
                    data=[
                        {'Dimension':'Largo Y', 'Valor':10},
                        {'Dimension':'Ancho X', 'Valor':10},
                    ],
                    editable=True,
                    row_deletable=False,
                    # style={
                    #     "marginTop": "20px"
                    # },
                )
            ], style={
                "margin": "40px 0px 50px 50px"
            }),
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "alignItems": "center",
        }),

        html.Div([
            
            html.Div([
                html.B("Datos de cuadricula X"),
                
                dash_table.DataTable(
                    id='tabla-cuadricula-x',
                    columns=[{
                        'name': i,
                        'id': i,
                        'deletable': True,
                        'renamable': True
                    } for i in ['Grid', 'Espaciado X']],
                    data=[
                        {i: 0 for i in ['Grid', 'Espaciado X']}
                        for j in range(3)

                    ],
                    editable=True,
                    row_deletable=True,
                    # style={
                    #     "marginTop": "20px"
                    # },
                ),

                html.Button('Agreg ar fila', id='editing-rows-button-X', n_clicks=0),
            ], style={
                "margin": "40px 0px 50px 50px"
            }),

            html.Div([
                html.B("Datos de cuadricula Y"),
                
                dash_table.DataTable(
                    id='tabla-cuadricula-y',
                    columns=[{
                        'name': i,
                        'id': i,
                        'deletable': True,
                        'renamable': True
                    } for i in ['Grid', 'Espaciado Y']],
                    data=[
                        {i: 0 for i in ['Grid', 'Espaciado Y']}
                        for j in range(3)

                    ],
                    editable=True,
                    row_deletable=True,
                    # style={
                    #     "marginTop": "20px"
                    # },
                ),
                
                html.Button('Agregar fila', id='editing-rows-button-Y', n_clicks=0),
            ], style={
                "margin": "40px 0px 50px 50px"
            }),
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "alignItems": "center",

        }),

        html.Div(
            id='container-button-basic',
            children=[
            html.Button('Grabar', id='grabar-datos', n_clicks=0),
                    
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "alignItems": "center",
            "marginTop": "50px",
        }),
    ]),

    html.Div([
        html.H1(children="Grafico")
    ], style={
        "display": "flex",
        "textAlign": "center",
        "justifyContent": "center",
        "alignItems": "center",
    }),

], style={
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": "space-between",
})


@callback(
    Output('tabla-cuadricula-x', 'data'),
    Input('editing-rows-button-X', 'n_clicks'),
    State('tabla-cuadricula-x', 'data'),
    State('tabla-cuadricula-x', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(
    Output('tabla-cuadricula-y', 'data'),
    Input('editing-rows-button-Y', 'n_clicks'),
    State('tabla-cuadricula-y', 'data'),
    State('tabla-cuadricula-y', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(
    Output('container-button-basic', 'children'),
    Input('grabar-datos', 'n_clicks'),
    State('tabla-cuadricula-x', 'data'),
    State('tabla-cuadricula-y', 'data'),
    prevent_initial_call=True)
def save_data(n_clicks, data_x, data_y):
    
    df_data_x = pd.DataFrame(data_x)
    df_data_y = pd.DataFrame(data_y)

    print(df_data_x)
    print(df_data_y)

    return 'CLICK'
    



if __name__ == '__main__':
    app.run(debug=True)