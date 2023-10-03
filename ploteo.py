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



def modelamiento_nodos(Nodes, Elems, Diap, df_x):
    # Generamos la malla
    RigidDiaphragm = 'ON'
    wipe()
    model('basic', '-ndm', 3, '-ndf', 6)
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
    imagen_01 = plt.savefig('foo.jpg')

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
    imagen_02 = plt.savefig("foo2.jpg")
    print("terminamos")

    return imagen_01 ,imagen_02



dataframe_x = pd.DataFrame({'Grid':[1,2,3,4], 'Espaciado':[1.5,1.5,2,0]})
dataframe_y = pd.DataFrame({'Grid':[1,2,3,4], 'Espaciado':[2,2,3,0]})
dataframe_z = pd.DataFrame({'Grid':[1,2,3,4], 'Espaciado':[2,1,1,0]})

# Nodos del Modelo
Nodes, Elems, Diap = GeoModel(dataframe_x, dataframe_y, dataframe_z)

modelamiento_nodos(Nodes, Elems, Diap, dataframe_x)