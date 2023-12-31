import numpy as np
from numpy import zeros
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import dash_auth
from PIL import Image
import math
from decimal import Decimal as D
import time

# import openseespy.opensees as ope
# import openseespyvis.Get_Rendering as opsplt
# import opsvis as opsv
# import openseespy.postprocessing.ops_vis as opsv
# import openseespy.postprocessing.Get_Rendering as opsplt

import warnings
warnings.filterwarnings("ignore")

# Own Development 
import functions as func 

# Autentification information
dff = pd.read_csv('zero.csv')
zero_auth = {}

for i in range(dff.shape[0]):
    zero_auth[dff['user'].iloc[i]] = dff['password'].iloc[i]


from dash import DiskcacheManager, CeleryManager
import os

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)


# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = zero_auth

app = Dash(__name__)
server = app.server

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

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
                    id='Analisis-sismico-dinamico',
                    columns=[{
                        'name': i,
                        'id': i,
                        'deletable': False,
                        'renamable': False
                    } for i in ['Factores', 'Valores']],
                    data=[
                        {'Factores':'Factor de Zona', 'Valores':0.45},
                        {'Factores':'Factor de Uso', 'Valores':1},
                        {'Factores':'Factor de suelo', 'Valores':1},
                        {'Factores':'Coef. Basico de Reducción', 'Valores':8},
                        {'Factores':'Tp', 'Valores':0.4},
                        {'Factores':'Tl', 'Valores':2.5},
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
                "margin": "10px 10px 10px"
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
                "margin": "10px 10px 10px"
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
                    html.H2("Datos de cuadrícula X", style={
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
                            "borderRadius": "14px",
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
                "margin": "20px 0px 20px"
            }),

            html.Div(children=[
                
                html.Div(children=[
                    html.H2("Datos de cuadrícula Y", style={
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
                            "borderRadius": "14px",
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
                "margin": "20px 0px 20px"
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
                            "borderRadius": "14px",
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
                "margin": "20px 0px 20px"
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
            
                html.Button('GENERAR RESULTADOS ', id='grabar-datos', n_clicks=0, 
                    style={
                        "alignItems": "center",
                        "appearance": "none",
                        "backgroundColor": "#15294b",
                        "borderRadius": "14px",
                        "borderStyle": "none",
                        "boxShadow": "rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0",
                        "boxSizing": "border-box",
                        "color": "white",
                        "cursor": "pointer",
                        "display": "inline-flex",
                        "fill": "currentcolor",
                        "fontFamily": "Roboto,Arial,sans-serif",
                        "fontSize": "14px",
                        "fontWeight": "bold",
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
            "justifyContent": "center",
            "width": "calc(100% - -15px)"
        }),
    # UPDATE max_dist
    html.Div([  
        html.Progress(id="progress_bar", value="0"),
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "padding": "2em 3em 2em 4em",
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
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    "paddingBottom": "0px",
                    "marginBottom": "0px"
                }),

                html.Div(children=[
                    dcc.Graph(id='plot-modelo-grillas', className="plot_modelo",style={"height": "80vh", "width": "80vh"})
                ]),
            ]),
            html.Div( children=[
                html.H2("MODELO DE VOLUMEN", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    "paddingBottom": "0px",
                    "marginBottom": "0px"
                }),
                dcc.Graph(id='plot-modelo-volumen', className="plot_modelo",style={"height": "80vh", "width": "80vh"})
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
            }, className="plot_container"),
    ]),

    # ------ ASIGNACION DE MASAS Y MODOS DE VIBRACION -----
    html.Div(children=[
        html.H2("ASIGNACIÓN DE MASAS Y MODOS DE VIBRACIÓN", style={
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
                html.H2("MODOS DE VIBRACIÓN", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                }),

                html.Div(children=[
                    dash_table.DataTable(
                        id="dataframe_Tmodes",
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
                    )
                ]),
            ]),

            html.Div( children=[
                html.H2("MATRIZ DE MASAS", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                }),
                
                html.Div(children=[
                    dash_table.DataTable(
                        id="analisis_masas", style_table={'overflowX': 'scroll'},
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
                    )
                ]),
            ], className="table_matriz_masas"),
            

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
            }, className="plot_container"),
    ]),

    # ----- ANALISIS ESTATICO EN X -----
    html.Div(children=[

        html.H2("ANÁLISIS ESTÁTICO EN X", style={
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
                html.H2("ANÁLISIS ESTÁTICO EN X", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                }),

                html.Div(children=[
                    dash_table.DataTable(
                        id="analisis_estatico_x",
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
                    )
                ]),
            ]),

            html.Div( children=[
                html.H2("PLOTEO DE DERIVAS EN X", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    "paddingBottom": "0px",
                    "marginBottom": "0px"
                }),

                html.Div(children=[
                    dcc.Graph(id='deformacion-x', className="plot",style={"height": "80vh", "width": "80vh"})

                ]),
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
        }, className="plot_container"),
    ]),

    # ----- ANALISIS ESTATICO EN Y -----
    html.Div(children=[

        html.H2("ANÁLISIS ESTÁTICO EN Y", style={
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
                html.H2("ANÁLSIS ESTÁTICO EN Y", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                }),

                html.Div(children=[
                    dash_table.DataTable(
                        id="analisis_estatico_y",
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
                    )
                ]),

            ]),
            html.Div( children=[
                html.H2("PLOTEO DE DERIVAS EN Y", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    "paddingBottom": "0px",
                    "marginBottom": "0px"
                }),
                
                html.Div(children=[
                    dcc.Graph(id='deformacion-y', className="plot",style={"height": "80vh", "width": "80vh"})

                ]),
                
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
        }, className="plot_container"),

    ]),

    # ----- MASAS EFECTIVIAS -----
    html.Div(children=[
        html.Div( children=[
            html.H2("MASAS EFECTIVAS", style={
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
                    dash_table.DataTable(
                        id="masas_efectivas",
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
                    )
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
            
        ]),
        
    ]),

    # RESULTADO FINAL 
    html.Div(children=[

        html.H2("ANÁLISIS DINÁMICO MODAL ESPECTRAL", style={
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
                    html.H2("ANÁLISIS DINÁMICO", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "paddingBottom": "15px",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                        "paddingBottom": "0px",
                        "marginBottom": "0px"
                    }),
                    html.Div(children=[
                        dash_table.DataTable(
                            id="analisis_final",
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
                        )
                    ]),
                ]),

                html.Div( children=[
                    html.H2("PLOTEO DE DISTORCIONES", style={
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "letterSpacing": "0",
                        "lineHeight": "1.5em",
                        "position": "relative",
                        "color": "#15294b",
                        "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                        "marginbottom": "0px"
                    }),
                    html.Div(children=[
                        dcc.Graph(id='plot-distorciones', className="plot_distorciones",style={"height": "80vh", "width": "80vh"})

                    ]),
                ]),

            ], style={
                "display": "flex",
                "textAlign": "center",
                "alignItems": "center"
            }, className="plot_container"),


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

    # ----- ANALISIS DE VIGAS Y COLUMNAS -----
    html.Div(children=[
        html.H2("DIMENSIONES DE ELEMENTOS", style={
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
                
                html.H2("VIGAS", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    "paddingBottom": "0px",
                    "marginBottom": "0px"
                }),

                html.Div( children=[
                    html.Div(children=[
                        dcc.Graph(id='vigas', className="plot",style={"height": "80vh", "width": "80vh"})# PLOT DE VIGA
                    ]),

                    html.Div( children=[
                        html.H2(" DIMENSIONES (b x h)", style={
                            "fontSize": "20px",
                            "fontWeight": "700",
                            "letterSpacing": "0",
                            "lineHeight": "1.5em",
                            "paddingBottom": "15px",
                            "position": "relative",
                            "color": "#15294b",
                            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                            "marginBottom": "0"
                        }),
                        
                        html.Div(children=[
                            html.Div(children=[
                                html.P("b: ", style={
                                    "fontSize": "20px",
                                    "fontWeight": "700",
                                    "letterSpacing": "0",
                                    "lineHeight": "1.5em",
                                    "position": "relative",
                                    "color": "#15294b",
                                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                                    "marginbottom": "0px"
                                }),
                                
                                html.P(id="base", style={"fontSize": "20px",}),
                            ], style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                            }),

                            html.Div(children=[
                                html.P("h: ", style={
                                    "fontSize": "20px",
                                    "fontWeight": "700",
                                    "letterSpacing": "0",
                                    "lineHeight": "1.5em",
                                    "position": "relative",
                                    "color": "#15294b",
                                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                                    "marginbottom": "0px"
                                }),
                                
                                html.P(id="altura", style={"fontSize": "20px",}),
                            ], style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                            }),                            
                        ]),
                    ], style={
                        "display": "flex",
                        "justifyContent": "center",
                        "textAlign": "center",
                        "flexDirection": "column",
                        "alignItems": "stretch",
                    }),
                ], style={
                    "display": "flex",
                    "justifyContent": "center",
                    "textAlign": "center",
                    "alignItems": "center"
                }, className="plot_container"),
                
                
            ], style={
                "display": "flex",
                "justifyContent": "center",
                "alignContent": "center",
                "alignItems": "center",
                "flexDirection": "column"
            }, className="plot_container"), 
            
            html.Div(children=[

                html.H2("COLUMNAS", style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "letterSpacing": "0",
                    "lineHeight": "1.5em",
                    "paddingBottom": "15px",
                    "position": "relative",
                    "color": "#15294b",
                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    "paddingBottom": "0px",
                    "marginBottom": "0px"
                }),

                html.Div( children=[

                    html.Div(children=[
                        dcc.Graph(id='columnas', className="plot",style={"height": "80vh", "width": "80vh"})# PLOT DE COLUMNAS
                      
                    ]),

                    html.Div( children=[
                        html.H2(" DIMENSIONES (a x a)", style={
                            "fontSize": "20px",
                            "fontWeight": "700",
                            "letterSpacing": "0",
                            "lineHeight": "1.5em",
                            "position": "relative",
                            "color": "#15294b",
                            "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                            "marginbottom": "0px"
                        }),
                        html.Div(children=[
                            html.Div(children=[
                                html.P("a: ", style={
                                    "fontSize": "20px",
                                    "fontWeight": "700",
                                    "letterSpacing": "0",
                                    "lineHeight": "1.5em",
                                    "position": "relative",
                                    "color": "#15294b",
                                    "fontFamily": "'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                                    "marginbottom": "0px"
                                }),
                                
                                html.P(id="area_1", style={"fontSize": "20px",}),
                            ], style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                            }),
                        ]),
                    ]),
                ], style={
                    "display": "flex",
                    "justifyContent": "center",
                    "textAlign": "center",
                    "alignItems": "center"
                }, className="plot_container"),
            ], style={
                "display": "flex",
                "justifyContent": "center",
                "textAlign": "center",
                "alignItems": "center",
                "flexDirection": "column"
            }, className="plot_container"),

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
    
    Output('dataframe_Tmodes', 'data'),
    Output('analisis_masas', 'data'),
    
    Output('analisis_estatico_x', 'data'),
    Output('deformacion-x', 'figure'),

    Output('analisis_estatico_y', 'data'),
    Output('deformacion-y', 'figure'),

    Output('masas_efectivas', 'data'),

    Output('analisis_final', 'data'),
    Output('plot-distorciones', 'figure'),

    
    Output('base', 'children'),
    Output('altura', 'children'),
    Output('area_1', 'children'),
    Output('columnas', 'figure'),
    Output('vigas', 'figure'),

    # INPUTS & STATES
    Input('grabar-datos', 'n_clicks'),
    State('tabla-cuadricula-x', 'data'),
    State('tabla-cuadricula-y', 'data'),
    State('tabla-cuadricula-z', 'data'),
    State('Analisis-sismico-dinamico', 'data'),
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    background=True,
    manager=background_callback_manager,
    prevent_initial_call=True)
def save_data(set_progress, n_clicks, data_x, data_y, data_z, data_sismico):
    set_progress((str(0), str(7)))

    df_x = pd.DataFrame(data_x).astype(float)
    df_y = pd.DataFrame(data_y).astype(float)
    df_z = pd.DataFrame(data_z).astype(float)
    df_sismico = pd.DataFrame(data_sismico)
    df_sismico['Valores'] = df_sismico['Valores'].astype(float)
    df_z.columns = ["Grid", "Espaciado"]
    
    # Predimencionamieno 1
    a, b, h, mini, L_max  = func.Predimencionamiento_1(df_x, df_y, df_z)
    
    # Generamos la malla
    Nodes, Elems, Diap = func.GeoModel(df_x, df_y, df_z)
    
    flag_last = 0
    first_dist = "ok"

    while 1:
        # Predimencionamieno 2
        Av,  Izv , Iyv, Jxxv, Ac, Izc, Iyc, Jxxc = func.Predimencionamiento_2(a, b, h)

        # Creacion de nodos y volumen
        func.ModelamientoNodos(Nodes, Elems, Diap, Ac, Jxxc, Iyc, Izc, Av, Jxxv, Iyv, Izv, a, b, h, flag_last)

        # Asignacion de masas y modos de vibracion
        Tmodes, MF, H, df_Tmodes= func.AsignacionMasasModosVibracion(Nodes, Elems, df_z, df_sismico)

        # Analisis estatico en X
        F, E030, df_estatico_x, fig_dist_x = func.AnalisisEstaticoX(Tmodes, MF, H, df_x, df_y, df_z, Diap, df_sismico, flag_last)

        # Analisis estatico en Y
        VS, df_estatico_y, fig_dist_y = func.AnalisisEstaticoY(Tmodes, MF, H,F, df_x, df_y, df_z, Diap, flag_last)

        # Masas efectivas
        ni, modo, Ux, Uy, Rz, df_masas_efectivas = func.MasasEfectivas(df_z, MF, Tmodes)

        # Analisis dinamico modal espectral
        nz = df_z.shape[0] - 1
        analisis_escalar, texto_generado, analisis_final, fig_dist, max_dist = func.AnalisisDinamicoModalEspectral(E030,MF,modo,Tmodes,nz,ni, Ux, Uy, Rz, VS, df_z, flag_last)
        
        # Consideramos la maxima distorsion entre estatico y dinamico
        max_dist = max([max_dist, float(df_estatico_x['DriftX(‰)'].max()), float(df_estatico_x['DriftY(‰)'].max()), float(df_estatico_y['DriftX(‰)'].max()), float(df_estatico_y['DriftY(‰)'].max())])

        if first_dist == "ok":
            first_dist = max_dist

        if max_dist > 7:
            set_progress((str(first_dist-max_dist), str(7)))
        else:
            set_progress((str(max_dist), str(7)))

        print("---------------------------")
        print(f'a:{a}, b:{b}, h:{h}')
        print("Max dist:", max_dist)
        print("---------------------------")
        
        var = D("0.01")
        if max_dist >= 6 and max_dist <= 7:
                break
            
        elif max_dist > 7:

            h = D(str(h)) + var
            
            b = h/D("2")
            if b < 0.20:
                b = 0.2

            a = D(str(a)) + var
            
        else:
        
            if h > mini:
                h = D(str(h)) - var
        
            b = D(str(h))/D("2")

            if b < 0.20:
                b = 0.2

            if a > 0.25:
                a = D(str(a)) - var

        a = float(a)
        b = float(b)
        h = float(h)

    flag_last = 1
    #----------------------------------------------------------------------------
    # Creacion de nodos y volumen
    func.ModelamientoNodos(Nodes, Elems, Diap, Ac, Jxxc, Iyc, Izc, Av, Jxxv, Iyv, Izv, a, b, h, flag_last)
    # Asignacion de masas y modos de vibracion
    Tmodes, MF, H, df_Tmodes= func.AsignacionMasasModosVibracion(Nodes, Elems, df_z, df_sismico)
    # Analisis estatico en X
    F, E030, df_estatico_x, fig_dist_x = func.AnalisisEstaticoX(Tmodes, MF, H, df_x, df_y, df_z, Diap, df_sismico, flag_last)
    # Analisis estatico en Y
    VS, df_estatico_y, fig_dist_y = func.AnalisisEstaticoY(Tmodes, MF, H,F, df_x, df_y, df_z, Diap, flag_last)
    # Masas efectivas
    ni, modo, Ux, Uy, Rz, df_masas_efectivas = func.MasasEfectivas(df_z, MF, Tmodes)
    # Analisis dinamico modal espectral
    nz = df_z.shape[0] - 1
    analisis_escalar, texto_generado, analisis_final, fig_dist, max_dist = func.AnalisisDinamicoModalEspectral(E030,MF,modo,Tmodes,nz,ni, Ux, Uy, Rz, VS, df_z, flag_last)
    #----------------------------------------------------------------------------

    print('------- Resultado final ----------')
    print(f'a:{a}, b:{b}, h:{h}')
    a_round = float(round(math.ceil(D(str(a)) / D(str(0.05))) * D(str(0.05)), 2))
    b_round = float(round(math.ceil(D(str(b)) / D(str(0.05))) * D(str(0.05)), 2))
    h_round = float(round(math.ceil(D(str(h)) / D(str(0.05))) * D(str(0.05)), 2))
    print(f'a:{a_round}, b:{b_round}, h:{h_round}')

    # ------ PLOTEO DEL MODELO -----
    # ----- PLOT GRILLAS -----
    img_modelo_grillas = Image.open('plots/modelo_grillas.jpg')
    fig_grillas = px.imshow(img = img_modelo_grillas)
    fig_grillas.update_layout(coloraxis_showscale=False) #, width=980, height=1089
    fig_grillas.update_xaxes(showticklabels=False)
    fig_grillas.update_yaxes(showticklabels=False)
    
    #  ----- MODELO VOLUMNE ------
    img_modelo_volumen = Image.open('plots/modelo_volumen.jpg')
    fig_volumen = px.imshow(img = img_modelo_volumen)
    fig_volumen.update_layout(coloraxis_showscale=False) # , width=980, height=1089
    fig_volumen.update_xaxes(showticklabels=False)
    fig_volumen.update_yaxes(showticklabels=False)
    
    # ------ ASIGNACION DE MASAS Y MODOS DE VIBRACION -----
    dataframe_Tmodes = df_Tmodes.to_dict("records")
    
    df_masas = pd.DataFrame(np.array(MF))
    df_masas = df_masas.round(4)
    dataframe_masas = df_masas.to_dict("records")

    # ------ ANALISIS ESTATICO EN X ------
    dataframe_estatico_x = df_estatico_x.to_dict("records")
    """
    img_estatico_x = Image.open("plots/deformacion_x.jpg")
    fig_estatico_x = px.imshow(img = img_estatico_x)
    fig_estatico_x.update_layout(coloraxis_showscale=False) # , width=980, height=1089
    fig_estatico_x.update_xaxes(showticklabels=False)
    fig_estatico_x.update_yaxes(showticklabels=False)
    """

    # ------ ANALISIS ESTATICO EN Y ------
    dataframe_estatico_y = df_estatico_y.to_dict("records")
    """
    img_estatico_y = Image.open("plots/deformacion_y.jpg")
    fig_estatico_y = px.imshow(img = img_estatico_y)
    fig_estatico_y.update_layout(coloraxis_showscale=False) # , width=980, height=1089
    fig_estatico_y.update_xaxes(showticklabels=False)
    fig_estatico_y.update_yaxes(showticklabels=False)
    """

    # ------ MASAS EFECTIVAS -----
    dataframe_masas_efectivas = df_masas_efectivas.to_dict("records")

    # ----- ANALISIS DINAMICO MODAL ESPECTRAL -----
    dataframe_escalar = analisis_escalar.to_dict("records")

    dataframe_final = analisis_final.to_dict("records")

    img_distorciones = Image.open("plots/distorsion_din.jpg")
    fig_distorciones = px.imshow(img = img_distorciones)
    fig_distorciones.update_layout(coloraxis_showscale=False) # , width=980, height=1089
    fig_distorciones.update_xaxes(showticklabels=False)
    fig_distorciones.update_yaxes(showticklabels=False)

    fig_columna, fig_viga = func.VigaColFinal(a_round, b_round, h_round, df_z, df_x, L_max)

    bb = str(b)+' ≈ '+str(b_round)
    aa = str(a)+' ≈ '+str(a_round)
    hh = str(h)+' ≈ '+str(h_round)

    set_progress((str(7), str(7)))
    return fig_grillas, fig_volumen, dataframe_Tmodes, dataframe_masas, dataframe_estatico_x, fig_dist_x, dataframe_estatico_y, fig_dist_y, dataframe_masas_efectivas, dataframe_final, fig_dist, bb, hh, aa, fig_columna, fig_viga



if __name__ == '__main__':
    app.run_server(debug=True)