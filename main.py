from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    
    html.Div([
            html.Div([

            html.Div([

                html.Div([
                    html.H2("Análisis Sísmico Dinamico", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#f0a500",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    })
                ]),
                
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
                    style_as_list_view=True,
                    style_cell={
                        'padding': '5px',
                        "textAlign": "center"
                        },
                    style_header={
                        'backgroundColor': '#9aa0a6',
                        'fontWeight': 'bold',
                        "color": "white",
                        "textAlign": "center"
                    },
                   
                )
            ], style={
                "margin": "40px 0px 50px 50px"
            }),
            
            html.Div([

                html.Div([
                    html.H2("Dimensiones de Terreno", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#f0a500",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    })
                ]),
                
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
                    style_as_list_view=True,
                    style_cell={
                        'padding': '5px',
                        "textAlign": "center"
                        },
                    style_header={
                        'backgroundColor': '#9aa0a6',
                        'fontWeight': 'bold',
                        "color": "white",
                        "textAlign": "center"
                    }
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
                
                html.Div([
                    html.H2("Datos de cuadricula X", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#f0a500",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    })
                ]),
                
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
                    style_as_list_view=True,
                    style_cell={
                        'padding': '5px',
                        "textAlign": "center"
                        },
                    style_header={
                        'backgroundColor': '#9aa0a6',
                        'fontWeight': 'bold',
                        "color": "white",
                        "textAlign": "center"
                    }
                    # style={
                    #     "marginTop": "20px"
                    # },
                ),

                html.Button('Agreg ar fila', id='editing-rows-button-X', n_clicks=0,
                            style={
                            "alignItems": "center",
                            "appearance": "none",
                            "backgroundColor": "#fff",
                            "borderRadius": "24px",
                            "borderStyle": "none",
                            "boxShadow": "rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0",
                            "boxSizing": "border-box",
                            "color": "#3c4043",
                            "cursor": "pointer",
                            "display": "inline-flex",
                            "fill": "currentcolor",
                            "fontFamily": "Roboto,Arial,sans-serif",
                            "fontSize": "14px",
                            "fontWeight": "500",
                            "height": "48px",
                            "justifyContent": "center",
                            "letterSpacing": ".25px",
                            "lineHeight": "normal",
                            "maxWidth": "100%",
                            "overflow": "visible",
                            "padding": "2px 24px",
                            "position": "relative",
                            "textAlign": "center",
                            "textTransform": "none",
                            "transition": "box-shadow 280ms cubic-bezier(.4, 0, .2, 1),opacity 15ms linear 30ms,transform 270ms cubic-bezie,(0, 0, .2, 1) 0ms",
                            "userSelect": "none",
                            "webkitUserSelect": "none",
                            "touchAction": "manipulation",
                            "width": "auto",
                            "willChange": "transform,opacity",
                            "zIndex": "0",
                        }),
            ], style={
                "margin": "40px 0px 50px 50px"
            }),

            html.Div([
                
                html.Div([
                    html.H2("Datos de cuadricula Y", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#f0a500",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    })
                ]),
                
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
                    style_as_list_view=True,
                    style_cell={
                        'padding': '5px',
                        "textAlign": "center"
                        },
                    style_header={
                        'backgroundColor': '#9aa0a6',
                        'fontWeight': 'bold',
                        "color": "white",
                        "textAlign": "center"
                    }
                    # style={
                    #     "marginTop": "20px"
                    # },
                ),
                
                html.Button('Agregar fila', id='editing-rows-button-Y', n_clicks=0,
                            style={
                            "alignItems": "center",
                            "appearance": "none",
                            "backgroundColor": "#fff",
                            "borderRadius": "24px",
                            "borderStyle": "none",
                            "boxShadow": "rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0",
                            "boxSizing": "border-box",
                            "color": "#3c4043",
                            "cursor": "pointer",
                            "display": "inline-flex",
                            "fill": "currentcolor",
                            "fontFamily": "Roboto,Arial,sans-serif",
                            "fontSize": "14px",
                            "fontWeight": "500",
                            "height": "48px",
                            "justifyContent": "center",
                            "letterSpacing": ".25px",
                            "lineHeight": "normal",
                            "maxWidth": "100%",
                            "overflow": "visible",
                            "padding": "2px 24px",
                            "position": "relative",
                            "textAlign": "center",
                            "textTransform": "none",
                            "transition": "box-shadow 280ms cubic-bezier(.4, 0, .2, 1),opacity 15ms linear 30ms,transform 270ms cubic-bezie,(0, 0, .2, 1) 0ms",
                            "userSelect": "none",
                            "webkitUserSelect": "none",
                            "touchAction": "manipulation",
                            "width": "auto",
                            "willChange": "transform,opacity",
                            "zIndex": "0",
                        }),
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
            html.Button('Grabar', id='grabar-datos', n_clicks=0, 
                        style={
                            "alignItems": "center",
                            "appearance": "none",
                            "backgroundColor": "#fff",
                            "borderRadius": "24px",
                            "borderStyle": "none",
                            "boxShadow": "rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0",
                            "boxSizing": "border-box",
                            "color": "#3c4043",
                            "cursor": "pointer",
                            "display": "inline-flex",
                            "fill": "currentcolor",
                            "fontFamily": "Roboto,Arial,sans-serif",
                            "fontSize": "14px",
                            "fontWeight": "500",
                            "height": "48px",
                            "justifyContent": "center",
                            "letterSpacing": ".25px",
                            "lineHeight": "normal",
                            "maxWidth": "100%",
                            "overflow": "visible",
                            "padding": "2px 24px",
                            "position": "relative",
                            "textAlign": "center",
                            "textTransform": "none",
                            "transition": "box-shadow 280ms cubic-bezier(.4, 0, .2, 1),opacity 15ms linear 30ms,transform 270ms cubic-bezie,(0, 0, .2, 1) 0ms",
                            "userSelect": "none",
                            "webkitUserSelect": "none",
                            "touchAction": "manipulation",
                            "width": "auto",
                            "willChange": "transform,opacity",
                            "zIndex": "0",
                        }),
                    
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "alignItems": "center",
            "marginTop": "50px",
        }),
    ], style={
        "maxWidth": "38em",
        "padding": "1em 3em 2em 3em",
        "margin": "2em 1em 1em 2em",
        "backgroundColor": "#fff",
        "borderRadius": "4.2px",
        "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
    }),

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
    "backgroundColor": "#b9b9b9"
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