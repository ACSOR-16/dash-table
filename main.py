import numpy as np
import pandas as pd
import plotly.express as px
from PIL import Image
from openseespy.opensees import wipe, model, node, fix, fixZ, geomTransf, element, rigidDiaphragm
import opsvis as opsv
import matplotlib.pyplot as plt
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
from numpy import zeros
import warnings
warnings.filterwarnings("ignore")
from ploteo import GeoModel, ModelamientoNodos

##
app = Dash(__name__)
#app.css.append_css({'/bWLwgP.css'})
# Análisis Sísmico Estático y Dinámico Modal Espectral
app.layout = html.Div(children=[
    html.H2("Análisis Sísmico Estático y Dinámico Modal Espectral", style={
                        "margin": "8px",
                        "display": "flex",
                        "justifyContent": "center",
                        "fontSize": "30px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "0px",
                        "marginBottom": "0px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }),
    html.Div(children=[
        html.Div(children=[
            html.Div(children=[

                html.Div(children=[
                    html.H2("Parametros Sísmicos", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
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
                        {'Factores':'Factor de Zona', 'Valores':1},
                        {'Factores':'Factor de Uso', 'Valores':0.45},
                        {'Factores':'Factor de suelo', 'Valores':1},
                        {'Factores':'Coef. Basico de Reducción', 'Valores':8},
                        {'Factores':'Tp', 'Valores':0.4},
                        {'Factores':'TI', 'Valores':2.5},
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
                "margin": "10px 10px 20px"
            }),
            
            html.Div(children=[

                html.Div(children=[
                    html.H2("Dimensiones de Terreno", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
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
                "margin": "10px 10px 20px"
            }),
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "alignItems": "center",
            "justifyContent": "space-evenly"
        }),

        html.Div(children=[
            
            html.Div(children=[
                
                html.Div(children=[
                    html.H2("Datos de cuadricula X", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
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
                    } for i in ['Grid', 'Espaciado']],
                    data=[
                        {i: 0 for i in ['Grid', 'Espaciado']}
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

                html.Button('Agregar fila', id='editing-rows-button-X', n_clicks=0,
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

            html.Div(children=[
                
                html.Div(children=[
                    html.H2("Datos de cuadricula Y", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
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
                    } for i in ['Grid', 'Espaciado']],
                    data=[
                        {i: 0 for i in ['Grid', 'Espaciado']}
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

            html.Div(children=[
                
                html.Div(children=[
                    html.H2("Datos de  elevación", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    })
                ]),
                
                dash_table.DataTable(
                    id='tabla-cuadricula-z',
                    columns=[{
                        'name': i,
                        'id': i,
                        'deletable': True,
                        'renamable': True
                    } for i in ['Nivel', 'Altura']],
                    data=[
                        {i: 0 for i in ['Nivel', 'Altura']}
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
                
                html.Button('Agregar fila', id='editing-rows-button-Z', n_clicks=0,
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
            })
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "space-evenly",
            "alignItems": "center",

        }),

        html.Div(
            id='container-button-basic',
            children=[
            html.Button('Generar Resultados', id='grabar-datos', n_clicks=0, 
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
        "maxWidth": "100%",
        "padding": "1em 3em 2em 3em",
        "margin": "1em  1em 2em",
        "backgroundColor": "#fff",
        "borderRadius": "4.2px",
        "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
    }),

    # ------PLOTEO DEL MODELO  -----
    html.Div(children=[
        html.H2("PLOTEO DEL MODELO", style={
            "fontSize": "20px",
            "fontWeight": "700",
            "letterSpacing": "0",
            "lineHeight": "1.5em",
            "position": "relative",
            "color": "#15294b",
            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            "textAlign": "center",
            "paddingBottom": "0px",
            "marginBottom": "0px"
        }),
        
        html.Div(children=[

            html.Div( children=[
                html.H2("MODELO DE NODOS", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),

                html.Div(children=[
                    # html.Img(src="./plots/modelo_grillas.jpg"),
                    dcc.Graph(id='plot-modelo-grillas')
                ]),
            ]),
            html.Div( children=[
                html.H2("MODELO DE VIGAS", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-volumen')
            ]),
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "space-evenly",
            "alignItems": "center",
            "maxWidth": "100%",
            "padding": "1em 3em 2em 3em",
            "margin": "0em  1em 2em",
            "backgroundColor": "#fff",
            "borderRadius": "4.2px",
            "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
            }),
    ]),

    # ------ ASIGNACION DE MASAS Y MODOS DE VIBRACION -----
    html.Div(children=[
        html.H2("ASIGNACION DE MASAS Y MODOS DE VIBRACION", style={
            "fontSize": "20px",
            "fontWeight": "700",
            "letterSpacing": "0",
            "lineHeight": "1.5em",
            "position": "relative",
            "color": "#15294b",
            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            "textAlign": "center",
            "marginBottom": "0px",
            "paddingBottom": "0px"
        }),

        html.Div(children=[

            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-grillas')
            ]),
            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-volumen')
            ]),
            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-volumen')
            ]),

        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "space-evenly",
            "alignItems": "center",
            "maxWidth": "100%",
            "padding": "1em 3em 2em 3em",
            "margin": "0em  1em 2em",
            "backgroundColor": "#fff",
            "borderRadius": "4.2px",
            "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
            }),
    ]),

    # ----- ANALISIS DE LA MATRIZ DE LAS MASAS -----
    html.Div(children=[
        html.Div( children=[
            html.H2("Analisis de la Matriz de Masas", style={
                "fontSize": "20px",
                "fontWeight": "700",
                "letterSpacing": "0",
                "lineHeight": "1.5em",
                "position": "relative",
                "color": "#15294b",
                "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
            }),
            dcc.Graph(id='plot-modelo-grillas')
        ]),
        
    ], style={
        "display": "flex",
        "textAlign": "center",
        "justifyContent": "center",
        "alignItems": "center",
        "maxWidth": "100%",
        "padding": "1em 3em 2em 3em",
        "margin": "0em  1em 2em",
        "backgroundColor": "#fff",
        "borderRadius": "4.2px",
        "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
    }),

    # ----- ANALISIS ESTATICO EN X -----
    html.Div(children=[

        html.H2("ANALISIS ESTATICO EN X", style={
            "fontSize": "20px",
            "fontWeight": "700",
            "letterSpacing": "0",
            "lineHeight": "1.5em",
            "position": "relative",
            "color": "#15294b",
            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            "textAlign": "center",
            "paddingBottom": "0px",
            "marginBottom": "0px",
        }),

        html.Div(children=[

            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-grillas')
            ]),
            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-volumen')
            ]),

        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "space-evenly",
            "alignItems": "center",
            "maxWidth": "100%",
            "padding": "1em 3em 2em 3em",
            "margin": "0em  1em 2em",
            "backgroundColor": "#fff",
            "borderRadius": "4.2px",
            "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
        }),
    ]),

    # ----- ANALISIS ESTATICO EN Y -----
    html.Div(children=[

        html.H2("ANALISIS ESTATICO EN Y", style={
            "fontSize": "20px",
            "fontWeight": "700",
            "letterSpacing": "0",
            "lineHeight": "1.5em",
            "position": "relative",
            "color": "#15294b",
            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            "textAlign": "center",
            "paddingBottom": "0px",
            "marginBottom": "0px"
        }),

        html.Div(children=[

            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-grillas')
            ]),
            html.Div( children=[
                html.H2("Grafico Nro", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                }),
                dcc.Graph(id='plot-modelo-volumen')
            ]),
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "space-evenly",
            "alignItems": "center",
            "maxWidth": "100%",
            "padding": "1em 3em 2em 3em",
            "margin": "0em  1em 2em",
            "backgroundColor": "#fff",
            "borderRadius": "4.2px",
            "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
        }),

    ]),

    # ----- ANALISIS DINAMICO MODAL ESPECTRAL -----
    html.Div(children=[

        html.H2("ANALISIS DINAMICO MODAL ESPECTRAL", style={
            "fontSize": "20px",
            "fontWeight": "700",
            "letterSpacing": "0",
            "lineHeight": "1.5em",
            "position": "relative",
            "color": "#15294b",
            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            "textAlign": "center",
            "paddingBottom": "0px",
            "marginBottom": "0px"
        }),

        html.Div(children=[

            html.Div(children=[

                html.Div( children=[
                    html.H2("Parrafo", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }),
                    html.Div(children=[
                        html.P("Al comparar la cortante basal obtenida en el análisis dinámico en X" 
                               "(1878.99 kN) y el 80% de la cortante basal del análisis estático en"
                                "X (1698.31 kN), se obtiene que NO es necesario escalar en X. En la"
                                 " dirección Y, la cortante basal obtenida en el análisis dinámico es "
                                 "1842.82 kN y el 80% de la cortante basal del análisis estático es 1698.31 kN. "
                                "Por lo que NO es necesario escalar en Y.")
                    ]),
                ]),

                html.Div( children=[
                    html.H2("ANÁLISIS DINÁMICO SIN ESCALAR", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }),
                    html.Div(children=[
                        # dcc.Graph(id='plot-modelo-volumen')
                        # DATAFRAME DE ANALISIS SIN ESCALAR

                    ]),
                ]),

            ]), 

            html.Div(children=[

                html.Div( children=[
                    html.H2("ANÁLISIS DINÁMICO FINAL", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }),
                    html.Div(children=[
                        # dcc.Graph(id='plot-modelo-volumen')
                        # DATA FRAME DE ANALISI DINAMICO
                    ]),
                ]),

                html.Div( children=[
                    html.H2("PLOTEO DE DISTORCIONES", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                    }),
                    html.Div(children=[
                        dcc.Graph(id='plot-modelo-volumen')

                    ]),
                ]),

            ], style={
                "display": "flex",
                "textAlign": "center",
            }),


        ], style={
            "display": "flex",
            "flexDirection": "column",
            "textAlign": "center",
            "justifyContent": "space-evenly",
            "alignItems": "center",
            "maxWidth": "100%",
            "padding": "1em 3em 2em 3em",
            "margin": "0em  1em 2em",
            "backgroundColor": "#fff",
            "borderRadius": "4.2px",
            "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
        }),
    ]),

], style={
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "space-between",
    "backgroundColor": "#F2F2F2"
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
    Output('tabla-cuadricula-z', 'data'),
    Input('editing-rows-button-Z', 'n_clicks'),
    State('tabla-cuadricula-z', 'data'),
    State('tabla-cuadricula-z', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(
    Output('plot-modelo-grillas', 'figure'),
    Output('plot-modelo-volumen', 'figure'),
    Input('grabar-datos', 'n_clicks'),
    State('tabla-cuadricula-x', 'data'),
    State('tabla-cuadricula-y', 'data'),
    State('tabla-cuadricula-z', 'data'),
    prevent_initial_call=True)
def save_data(n_clicks, data_x, data_y, data_z):
    df_x = pd.DataFrame(data_x).astype(float)
    df_y = pd.DataFrame(data_y).astype(float)
    df_z = pd.DataFrame(data_z).astype(float)
    df_z.columns = ["Grid", "Espaciado"]

    # Generamos la malla
    Nodes, Elems, Diap, start_viga_x, end_viga_x = GeoModel(df_x, df_y, df_z)
    #print(Nodes)
    #print(Elems)
    #print(Diap)
    # Creacion de nodos y volumen
    ModelamientoNodos(Nodes, Elems, Diap, df_x, start_viga_x, end_viga_x)

    # Plot grillas y modelo volumen
    img_modelo_grillas = Image.open('plots/modelo_grillas.jpg')
    fig_grillas = px.imshow(img = img_modelo_grillas)
    fig_grillas.update_layout(coloraxis_showscale=False, width=980, height=1089)
    fig_grillas.update_xaxes(showticklabels=False)
    fig_grillas.update_yaxes(showticklabels=False)

    img_modelo_volumen = Image.open('plots/modelo_volumen.jpg')
    fig_volumen = px.imshow(img = img_modelo_volumen)
    fig_volumen.update_layout(coloraxis_showscale=False, width=980, height=1089)
    fig_volumen.update_xaxes(showticklabels=False)
    fig_volumen.update_yaxes(showticklabels=False)
    
    return fig_grillas, fig_volumen


if __name__ == '__main__':
    app.run(debug=True)