import numpy as np
import pandas as pd
from openseespy.opensees import wipe, model, node, fix, fixZ, geomTransf, element, rigidDiaphragm
import openseespy.postprocessing.ops_vis as opsv
import matplotlib.pyplot as plt
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
from numpy import zeros

# ---- SISTEMA DE UNIDADES ----
# Unidades Base
m = 1
kg = 1
s = 1
# Otras Unidades
cm = 0.01*m
N = kg*m/s**2
kN = 1000*N
kgf = 9.80665*N
tonf = 1000*kgf
Pa = N/m**2
# Constantes Físicas
g = 9.80665*m/s**2

# ---- PROPIEDADES DEL MATERIAL Y DE SECCIONES ----
fc = 210*kg/cm**2
E = 151*fc**0.5*kgf/cm**2
G = 0.5*E/(1+0.2)
# Viga
b,h = 30*cm, 60*cm
Av = b*h
Izv = b*h**3/12
Iyv = b**3*h/12
aa, bb = max(b,h),min(b,h)
β= 1/3-0.21*bb/aa*(1-(bb/aa)**4/12)
Jxxv = β*bb**3*aa
# Columna
a = 60*cm
Ac = a**2
Izc = a**4/12
Iyc = a**4/12
β= 1/3-0.21*1.*(1-(1.)**4/12)
Jxxc = β*a**4
# Densidad del concreto
ρ = 2400*kg/m**3

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
                        {'Factores':"f'c Concreto", 'Valores':210},
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
                "margin": "10px 10px 20px"
            }),
        ], style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "alignItems": "center",
            "justifyContent": "space-evenly"
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

            html.Div([
                
                html.Div([
                    html.H2("Datos de cuadricula Z", style={
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
                    id='tabla-cuadricula-z',
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
        "maxWidth": "100%",
        "padding": "1em 3em 2em 3em",
        "margin": "1em  1em 2em",
        "backgroundColor": "#fff",
        "borderRadius": "4.2px",
        "boxShadow": "0px 3px 10px -2px rgba(0, 0, 0, 0.2)",
    }),

    html.Div([
        html.H1(children="Grafico"),
        html.Div([html.Img(src="./foo.jpg")]),
        html.Div([html.Img(src="./foo2.jpg")]),
    ], style={
        "display": "flex",
        "textAlign": "center",
        "justifyContent": "center",
        "alignItems": "center",
    }),

], style={
    "display": "flex",
    "flexDirection": "column",
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
    Output('tabla-cuadricula-z', 'data'),
    Input('editing-rows-button-Z', 'n_clicks'),
    State('tabla-cuadricula-z', 'data'),
    State('tabla-cuadricula-z', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(
    Output('container-button-basic', 'children'),
    Input('grabar-datos', 'n_clicks'),
    State('tabla-cuadricula-x', 'data'),
    State('tabla-cuadricula-y', 'data'),
    State('tabla-cuadricula-z', 'data'),
    prevent_initial_call=True)


def save_data(n_clicks, data_x, data_y, data_z):
    df_x = pd.DataFrame(data_x)
    df_y = pd.DataFrame(data_y)
    df_z = pd.DataFrame(data_z)

    # ---- CREACION DEL MODELO ----
    def GeoModel(df_x, df_y, df_z):
        Lx, Ly, Lz = df_x["Espaciado"].sum(), df_y["Espaciado"].sum(), df_z["Espaciado"].sum()
        NN = (df_x.shape[0])*(df_y.shape[0])*(df_z.shape[0])
        Nodes = zeros((NN,5))
        # Creando los nodos y asignando coordenadas
        c = 0
        for z in range(df_z.shape[0]):
            for y in range(df_y.shape[0]):
                for x in range(df_x.shape[0]):

                    Nodes[c] = [c, float(df_x["Espaciado"].iloc[:x].sum()), float(df_y["Espaciado"].iloc[:y].sum()), float(df_z["Espaciado"].iloc[:z].sum()), 0.5]
                    c += 1


        Nodes[:(df_x.shape[0])*(df_y.shape[0]),4]=0
        # print(Nodes)

        NE = ((df_x.shape[0]-1)*(df_y.shape[0])+(df_y.shape[0]-1)*(df_x.shape[0])+(df_x.shape[0])*(df_y.shape[0]))*(df_z.shape[0]-1)
        Elems = zeros((NE,4))
        # # Creando las conexiones de los elementos verticales
        c = 0
        for i in range((df_z.shape[0]-1)):
            for j in range(df_y.shape[0]):
                for k in range(df_x.shape[0]):
                    Elems[c] = [c,c,c+(df_x.shape[0])*(df_y.shape[0]),1]
                    c = c + 1
        # # Creando las conexiones de los elementos horizontales
        m = (df_x.shape[0])*(df_y.shape[0])
        for i in range(df_z.shape[0]-1):
            for j in range(df_y.shape[0]):
                for k in range(df_x.shape[0]-1):
                    Elems[c] = [c,m,m+1,2]
                    m = m + 1
                    c = c + 1
                m = m + 1
        # # Creando las conexiones de los elementos horizontales
        n = 0
        for i in range(df_z.shape[0]-1):
            n = n + (df_x.shape[0])*(df_y.shape[0])
            for j in range(df_x.shape[0]):
                for k in range(df_y.shape[0]-1):
                    Elems[c] = [c,j+k*(df_x.shape[0])+n,j+(df_x.shape[0])+k*(df_x.shape[0])+n,2]
                    c = c + 1
        # # Creando centro de diafragmas
        Diap = zeros((df_z.shape[0]-1, 4))
        for i in range(df_z.shape[0]-1):
            Diap[i] = [i+1000, Lx/2.0, Ly/2.0, (df_z["Espaciado"].iloc[:i+1].sum())]

        print("S")
        return Nodes, Elems, Diap

    wipe()
    model('basic', '-ndm', 3, '-ndf', 6)

    # Generamos la malla
    RigidDiaphragm = 'ON'
    print(df_x)
    print(df_y)
    print(df_z)
    # Nodos del Modelo
    Nodes, Elems, Diap = GeoModel(df_x, df_y, df_z)


    #  ----- CREANDO NODOS DEL MODELO ----
    for Ni in Nodes:
    # print(Ni)
        node(int(Ni[0]), *Ni[1:4])

    # Definimos diafragmas rígidos
    if RigidDiaphragm == 'ON':
        dirDia = 3 # perpendicular al plano del diafragma
        for Nd in Diap:
            node(int(Nd[0]), *Nd[1:4])
            fix(int(Nd[0]),*[0,0,1,1,1,0])
            NodesDi = []
            for Ni in Nodes:
                if Ni[3]==Nd[3]:
                    NodesDi.append(int(Ni[0]))
            print(dirDia,int(Nd[0]),*NodesDi)
            rigidDiaphragm(int(dirDia),int(Nd[0]),*NodesDi)

    print('HERE')
    # ----- ASIGNAMOS RESTRICCIONES EN LOS NODOS ----
    # Restricciones
    fixZ(0.0, *[1,1,1,1,1,1], '-tol', 1e-6)

    # ----- ESTABLECEMOS UNA TRANSFORMACION GEOMETRICA
    geomTransf('PDelta', 1, *[1, 0, 0])
    geomTransf('Linear', 2, *[1,-1, 0])

    # ---- ESTABLECEMOS LOS ELEMENTOS CON SUS PROPIEDADES RESPECTIVAS
    # Creamos los elementos
    for Ele in Elems:
        if int(Ele[3]) == 1:# 1 Columna
            element('elasticBeamColumn', int(Ele[0]), int(Ele[1]), int(Ele[2]), Ac, E, G, Jxxc, Iyc, Izc, int(Ele[3]),'-mass', ρ*Ac)
        else: # 2 Viga
            # for x in range(df_x.shape[0]+1):
            element('elasticBeamColumn', int(Ele[0]), int(Ele[1]), int(Ele[2]), Av, E, G, Jxxv, Iyv, Izv, int(Ele[3]),'-mass', ρ*Av*((df_x["Espaciado"].iloc[0:-1].mean())-a)/(df_x["Espaciado"].iloc[0:-1].mean()))

    # ------ PLOTEO DEL MODELO ----
    plt.figure() # dpi=600
    opsv.plot_model(fig_wi_he=(30., 40.),az_el=(-130,20), )
    plt.savefig('foo.jpg')

    ele_shapes = {}
    for i in range(len(Elems)):
        if int(Elems[i,3])==1: # Column
            ele_shapes[i] = ['rect', [a, a]]
        elif int(Elems[i,3])==2: # Beam
            ele_shapes[i] = ['rect', [b, h]]
        else:
            print('Error. No es ni elemento viga ni columna.')
    plt.figure()
    opsv.plot_extruded_shapes_3d(ele_shapes, fig_wi_he=(40.0, 32.0), az_el=(-130,20),fig_lbrt = (0, 0, 1, 1))
    plt.savefig("foo2.jpg")

    
    
# ---------- COLAB -------------
# wipe, model, node, fix, fixZ, geomTransf, element


# plt.axis([0,nx*dx,0,ny*dy])

if __name__ == '__main__':
    app.run(debug=True)