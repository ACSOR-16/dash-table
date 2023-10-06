import numpy as np
import pandas as pd
import openseespy.opensees as ope
import openseespyvis.Get_Rendering as opsplt
import opsvis as opsv
import matplotlib.pyplot as plt
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
from numpy import zeros
from PIL import Image, ImageChops

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

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

# ---- CREACION DEL MODELO ----
def GeoModel(df_x, df_y, df_z):
    ope.wipe()
    ope.model('basic', '-ndm', 3, '-ndf', 6)

    Lx = df_x["Espaciado"].sum()
    Ly = df_y["Espaciado"].sum()
    Lz = df_z["Espaciado"].sum()
    NN = (df_x.shape[0])*(df_y.shape[0])*(df_z.shape[0])
    Nodes = zeros((NN,5))

    len_x = df_x.shape[0]
    len_y = df_y.shape[0]
    len_z = df_z.shape[0]    
    # Creando los nodos y asignando coordenadas 
    c = 0
    for z in range(len_z):
        for y in range(len_y):
            for x in range(len_x):
                if (x == 0 or x == len_x - 1) and (y == 0 or y == len_y - 1):
                    Nodes[c] = [c, df_x["Espaciado"].iloc[:x].sum(), df_y["Espaciado"].iloc[:y].sum(), df_z["Espaciado"].iloc[:z].sum(), 0.25]
                elif (y == 0 or y == len_x - 1) and (x != 0 or x != len_x - 1): 
                    Nodes[c] = [c, df_x["Espaciado"].iloc[:x].sum(), df_y["Espaciado"].iloc[:y].sum(), df_z["Espaciado"].iloc[:z].sum(), 0.5]
                elif (x == 0 or x == len_x - 1) and (y != 0 or y != len_y - 1):
                    Nodes[c] = [c, df_x["Espaciado"].iloc[:x].sum(), df_y["Espaciado"].iloc[:y].sum(), df_z["Espaciado"].iloc[:z].sum(), 0.5]
                else:
                    Nodes[c] = [c, df_x["Espaciado"].iloc[:x].sum(), df_y["Espaciado"].iloc[:y].sum(), df_z["Espaciado"].iloc[:z].sum(), 1]
            
                c += 1


    # primer piso carga en nodos es = Cero
    Nodes[:(len_x)*(len_y),4]=0
    # print(Nodes)

    NE = ((len_x-1)*(len_y)+(len_y-1)*(len_x)+(len_x)*(len_y))*(len_z-1)
    Elems = zeros((NE,5))
    # # Creando las conexiones de los elementos verticales
    c = 0
    for i in range((len_z-1)):
        for j in range(len_y):
            for k in range(len_x):
                Elems[c] = [c,c,c+(len_x)*(len_y),1, 0]
                c = c + 1
    # # Creando las conexiones de los elementos horizontales en X
    m = (len_x)*(len_y)
    for i in range(len_z-1):
        for j in range(len_y):
            for k in range(len_x-1):
                Elems[c] = [c,m,m+1,2, df_x["Espaciado"].iloc[k]]
                m = m + 1
                c = c + 1
            m = m + 1

    # # Creando las conexiones de los elementos horizontales en Y
    n = 0
    for i in range(len_z-1):
        n = n + (len_x)*(len_y)
        for j in range(len_x):
            for k in range(len_y-1):
                Elems[c] = [c,j+k*(len_x)+n,j+(len_x)+k*(len_x)+n,3, df_y["Espaciado"].iloc[k]]
                c = c + 1
    
    # # Creando centro de diafragmas
    Diap = zeros((len_z-1, 4))
   
    for i in range(len_z-1):
        Diap[i] = [i+1000, Lx/2.0, Ly/2.0, (df_z["Espaciado"].iloc[:i+1].sum())]

    return Nodes, Elems, Diap



def ModelamientoNodos(Nodes, Elems, Diap):
    
    RigidDiaphragm = 'ON'
    #  ----- CREANDO NODOS DEL MODELO ----
    for Ni in Nodes:
    # print(Ni)
        ope.node(int(Ni[0]), *Ni[1:4])

    # Definimos diafragmas rígidos
    if RigidDiaphragm == 'ON':
        dirDia = 3 # perpendicular al plano del diafragma
        for Nd in Diap:
            ope.node(int(Nd[0]), *Nd[1:4])
            ope.fix(int(Nd[0]),*[0,0,1,1,1,0])
            NodesDi = []
            for Ni in Nodes:
                if Ni[3]==Nd[3]:
                    NodesDi.append(int(Ni[0]))
            #print(dirDia,int(Nd[0]),*NodesDi)
            ope.rigidDiaphragm(int(dirDia),int(Nd[0]),*NodesDi)

    # ----- ASIGNAMOS RESTRICCIONES EN LOS NODOS ----
    # Restricciones
    ope.fixZ(0.0, *[1,1,1,1,1,1], '-tol', 1e-6)

    # ----- ESTABLECEMOS UNA TRANSFORMACION GEOMETRICA
    ope.geomTransf('PDelta', 1, *[1, 0, 0])
    ope.geomTransf('Linear', 2, *[1,-1, 0])
    ope.geomTransf('Linear', 3, *[1,-1, 0])

    # ---- ESTABLECEMOS LOS ELEMENTOS CON SUS PROPIEDADES RESPECTIVAS
    # Creamos los elementos
    for Ele in Elems:
        if int(Ele[3]) == 1:# 1 Columna
            ope.element('elasticBeamColumn', int(Ele[0]), int(Ele[1]), int(Ele[2]), Ac, E, G, Jxxc, Iyc, Izc, int(Ele[3]),'-mass', ρ*Ac)
        else: # 2 Viga
            ope.element('elasticBeamColumn', int(Ele[0]), int(Ele[1]), int(Ele[2]), Av, E, G, Jxxv, Iyv, Izv, int(Ele[3]),'-mass', ρ*Av*((Ele[4]-a)/Ele[4])) # ρ*Av*((dx-a)/dx))  #  #ρ*Av*(dy-a)/dy) # considerarr cuanndo la viga esta en x o y

    # ------ PLOTEO DEL MODELO ----
    plt.figure() # dpi=600
    opsv.plot_model(fig_wi_he=(30., 40.),az_el=(-130,20), )
    plt.savefig('plots/modelo_grillas.jpg')
    im = Image.open('plots/modelo_grillas.jpg')
    im = trim(im)
    im.save('plots/modelo_grillas.jpg')

    ele_shapes = {}
    for i in range(len(Elems)):
        if int(Elems[i,3])==1: # Column
            ele_shapes[i] = ['rect', [a, a]]
        elif int(Elems[i,3])==2 or int(Elems[i,3])==3: # Beam
            ele_shapes[i] = ['rect', [b, h]]
        else:
            print('Error. No es ni elemento viga ni columna.')
    
    plt.figure()
    opsv.plot_extruded_shapes_3d(ele_shapes, fig_wi_he=(40.0, 32.0), az_el=(-130,20),fig_lbrt = (0, 0, 1, 1))
    plt.savefig("plots/modelo_volumen.jpg")
    im = Image.open("plots/modelo_volumen.jpg")
    im = trim(im)
    im.save("plots/modelo_volumen.jpg")



def EspectroE030(T,Z=0.45,U=1.5,S=1.0,Tp=0.4,Tl=2.5,R=1):
    n = len(T)
    E030 = zeros(n)
    for i in range(n):
        if T[i]>=0 and T[i]<0.2*Tp:
            E030[i]=2.5#1+7.5*T[i]/Tp
        elif T[i]>=0.2*Tp and T[i]<Tp:
            E030[i]=2.5
        elif T[i]>=Tp and T[i]<Tl:
            E030[i] = 2.5*(Tp/T[i])
        elif T[i]>=Tl:
            E030[i] = 2.5*(Tp*Tl/T[i]**2)
        else:
            print("El periodo no puede ser negativo!")
    return E030*Z*U*S/R



def GetStaticLoads(coef,p,h,T):
    n = len(h)
    V = coef*sum(p)
    F = zeros(n)
    #
    if T > 0.0 and T <= 0.5:
        k=1.0
    elif T>0.5:
        k = 0.75+0.5*T
    else:
        print('El periodo es negativo!')
    #
    div = 0.
    for i in range(n):
        div = div + p[i]*h[i]**k
    #
    for i in range(n):
        F[i] = p[i]*h[i]**k/div*V
    return F,k


def AsignacionMasasModosVibracion(Nodes, Elems, df_z):
    # Aplicando Cargas vivas y muertas
    wLive = 250*kg/m**2
    wLosa = 300*kg/m**2
    wAcab = 100*kg/m**2
    wTabi = 150*kg/m**2
    wTotal = 1.0*(wLosa+wAcab+wTabi)+0.25*wLive

    df_E = pd.DataFrame(Elems, columns = ['n_element', 'node_1', 'node_2', 'col_viga','espaciado'])
    
    for Ni in Nodes:
        # Base
        if Ni[4] == 0:
            ope.mass(int(Ni[0]),0.0,0.0,0.0)
        # Esquinero
        elif Ni[4] == 0.25:
            xx = (df_E[((df_E['node_1']==Ni[0])|(df_E['node_2']==Ni[0]))&(df_E['col_viga']==2)]['espaciado']/2).sum()
            yy = (df_E[((df_E['node_1']==Ni[0])|(df_E['node_2']==Ni[0]))&(df_E['col_viga']==3)]['espaciado']/2).sum()
            carga = wTotal*xx*yy
            ope.mass(int(Ni[0]), carga, carga,0.0)
        # Perimetrales
        elif Ni[4] == 0.5:
            xx = (df_E[((df_E['node_1']==Ni[0])|(df_E['node_2']==Ni[0]))&(df_E['col_viga']==2)]['espaciado']/2).sum()
            yy = (df_E[((df_E['node_1']==Ni[0])|(df_E['node_2']==Ni[0]))&(df_E['col_viga']==3)]['espaciado']/2).sum()
            carga = wTotal*xx*yy
            ope.mass(int(Ni[0]), carga, carga,0.0)
        # Centrales
        else:
            xx = (df_E[((df_E['node_1']==Ni[0])|(df_E['node_2']==Ni[0]))&(df_E['col_viga']==2)]['espaciado']/2).sum()
            yy = (df_E[((df_E['node_1']==Ni[0])|(df_E['node_2']==Ni[0]))&(df_E['col_viga']==3)]['espaciado']/2).sum()
            carga = wTotal*xx*yy
            ope.mass(int(Ni[0]), carga, carga,0.0)

    # Obtenemos los modos
    Nmodes = 12

    # ploteamos el modos de vibracion
    """
    plt.figure()
    opsplt.plot_modeshape(1, 100)
    plt.savefig('plots/vibracion_1.jpg')
    plt.figure()
    opsplt.plot_modeshape(2, 100)
    plt.savefig('plots/vibracion_2.jpg')
    plt.figure()
    opsplt.plot_modeshape(3, 100)
    plt.savefig('plots/vibracion_3.jpg')
    """
    # Generacion de Tmodes 
    vals = ope.eigen(Nmodes)
    #vals = ope.eigen('-fullGenLapack',Nmodes)
    Tmodes = np.zeros(len(vals))
    for i in range(Nmodes):
        Tmodes[i] = 2*np.pi/vals[i]**0.5
        
    df_Tmodes = pd.DataFrame({'n_mode':[i+1 for i in range(len(Tmodes))], 'Tmode':Tmodes})

    # Realizamos un análisis para obtener la matriz de Masas
    ope.wipeAnalysis()
    ope.system('FullGeneral')
    ope.numberer("Plain")
    ope.constraints('Transformation')
    ope.algorithm('Linear')
    ope.analysis('Transient')
    ope.integrator('GimmeMCK',1.0,0.0,0.0)
    ope.analyze(1,0.0, )

    # Obtenemos la matriz de Masas
    nz = df_z.shape[0] - 1
    N = ope.systemSize()         # Número de Grados de Libertad
    Mmatrix = ope.printA('-ret')
    Mmatrix = np.array(Mmatrix).reshape((N,N))
    MF = Mmatrix[-3*nz:,-3*nz:]
    
    np.set_printoptions(precision=3,linewidth=300,suppress=True)
    #print(MF)
    H = np.array([df_z['Espaciado'].iloc[:i+1].sum() for i in  range(df_z.shape[0]-1)])
    P = sum(MF[0::3,0::3])*9.80665 # Peso por nivel
    #print(H,P)
    Ro = 8.
    E030 = EspectroE030(Tmodes,Z=0.45,U=1.0,S=1.0,Tp=0.4,Tl=2.5,R=Ro)
    F, k = GetStaticLoads(E030[0],P,H,Tmodes[0])
    #print(E030[0],k)

    return Tmodes, MF, H

def AnalisisEstaticoX(Tmodes, MF, H, df_x, df_y, df_z, Diap):
    np.set_printoptions(precision=3,linewidth=300,suppress=True)
    #H = np.arange(1,nz+1)*dz
    P = sum(MF[0::3,0::3])*9.80665 # Peso por nivel
    #print(H,P)
    Ro = 8.
    E030 = EspectroE030(Tmodes,Z=0.45,U=1.0,S=1.0,Tp=0.4,Tl=2.5,R=Ro)
    F, k = GetStaticLoads(E030[0],P,H,Tmodes[0])
    CR = E030[0]/(0.45*1.*1.)
    #print('C/R=',CR)
    #print(E030[0],k)
    
    # Aplicando fuerzas estáticas en X
    ope.timeSeries('Linear',1)
    ope.pattern('Plain',1,1)
    Le = df_y['Espaciado'].sum() * 0.05 # ny*dy*0.05  
    for i in range(len(H)):
        ope.load(int(Diap[i][0]),F[i],0.,0.,0.,0.,F[i]*Le)

    ope.wipeAnalysis()
    ope.constraints('Transformation')
    ope.numberer('Plain')
    ope.system('FullGeneral')
    ope.algorithm('Linear')
    ope.integrator('LoadControl',1)
    ope.analysis('Static')
    ope.analyze(1)

    # Calculos cortantes
    VS = np.cumsum(F[::-1])[::-1]

    ''' Resultados de analisis estatico en X '''
    # Desplazamientos
    df1_x = pd.DataFrame({'Nivel':[],'Vx(kN)':[],'UxMax(cm)':[],'UyMax(cm)':[],'DriftX(‰)':[],'DriftY(‰)':[]})
    tempX, tempY = 0., 0.
    for i in range(len(H)):
        desX = ope.nodeDisp(int(Diap[i][0]),1)
        desY = ope.nodeDisp(int(Diap[i][0]),2)
        rotZ = ope.nodeDisp(int(Diap[i][0]),6)
        desX = desX + abs(rotZ*df_y['Espaciado'].sum()/2)
        desY = desY + abs(rotZ*df_x['Espaciado'].sum()/2)
        desX, desY = desX*0.75*Ro, desY*0.75*Ro
        driftX = 1000.*(desX-tempX)/df_z['Espaciado'].iloc[i]  # altura de cada piso
        driftY = 1000.*(desY-tempY)/df_z['Espaciado'].iloc[i]
        tempX, tempY = desX, desY
        df2_x = pd.DataFrame({'Nivel':[i+1],'Vx(kN)':[VS[i]/1000],'UxMax(cm)':[desX*100],'UyMax(cm)':[desY*100],'DriftX(‰)':[driftX],'DriftY(‰)':[driftY]})
        df1_x = pd.concat([df1_x, df2_x])
    #print('\nANÁLISIS ESTÁTICO EN X')
    #print(df1_x.round(4))
    plt.figure()
    opsv.plot_defo(1000,fig_wi_he=(30., 25.),az_el=(-130,20))
    plt.savefig("plots/deformacion_x.jpg")

    return F, E030
    

def AnalisisEstaticoY(Tmodes, MF, H,F, df_x, df_y, df_z, Diap):
    ope.loadConst('-time', 0.0)
    ope.remove('timeSeries',1)
    ope.remove('loadPattern',1)
    ope.timeSeries('Linear',1)
    ope.pattern('Plain',1,1)
    Le = df_x['Espaciado'].sum() * 0.05 # nx*dx*0.05

    for i in range(len(H)):
        ope.load(int(Diap[i][0]),0.,F[i],0.,0.,0.,F[i]*Le)

    ope.wipeAnalysis()
    ope.constraints('Transformation')
    ope.numberer('Plain')
    ope.system('FullGeneral')
    ope.algorithm('Linear')
    ope.integrator('LoadControl',1)
    ope.analysis('Static')
    ope.analyze(1)

    VS = np.cumsum(F[::-1])[::-1]

    ''' Resultados de analisis estatico en Y '''
    # Desplazamientos
    df1_y = pd.DataFrame({'Nivel':[],'Vy(kN)':[],'UxMax(cm)':[],'UyMax(cm)':[],'DriftX(‰)':[],'DriftY(‰)':[]})
    tempX, tempY = 0., 0.
    Ro = 8.
    for i in range(len(H)):
        desX = ope.nodeDisp(int(Diap[i][0]),1)
        desY = ope.nodeDisp(int(Diap[i][0]),2)
        rotZ = ope.nodeDisp(int(Diap[i][0]),6)
        desX = desX + abs(rotZ*df_y['Espaciado'].sum()/2)
        desY = desY + abs(rotZ*df_x['Espaciado'].sum()/2)
        desX, desY = desX*0.75*Ro, desY*0.75*Ro
        driftX = 1000.*(desX-tempX)/df_z['Espaciado'].iloc[i]  # altura de cada piso
        driftY = 1000.*(desY-tempY)/df_z['Espaciado'].iloc[i]
        tempX, tempY = desX, desY
        df2_y = pd.DataFrame({'Nivel':[i+1],'Vy(kN)':[VS[i]/1000],'UxMax(cm)':[desX*100],'UyMax(cm)':[desY*100],'DriftX(‰)':[driftX],'DriftY(‰)':[driftY]})
        df1_y = pd.concat([df1_y, df2_y])
    #print('\nANÁLISIS ESTÁTICO EN Y')
    #print(df1_y.round(4))
    plt.figure()
    opsv.plot_defo(1000,fig_wi_he=(30., 25.),az_el=(-130,20))
    plt.savefig("plots/deformacion_y.jpg")

    return VS


def MasasEfectivas(df_z, MF, Tmodes):

    Tags = ope.getNodeTags()
    nz = int(df_z.shape[0]-1)
    Nmodes = 12
    modo = np.zeros((Nmodes,3*nz))

    for j in range(1,Nmodes+1):
        ind = 0
        for i in Tags[-nz:]:
            temp = ope.nodeEigenvector(i,j)
            modo[j-1,[ind,ind+1,ind+2]] = temp[0],temp[1],temp[-1]
            ind = ind + 3
  
    # Definimos valores iniciales
    Ux,Uy,Rz = np.zeros(3*nz),np.zeros(3*nz),np.zeros(3*nz)
    Ux[0::3]=1
    Uy[1::3]=1
    Rz[2::3]=1
    SUMx, SUMy, SUMr = 0., 0., 0.
    ni = 0

    Mx = sum(sum(MF[0::3,0::3]))
    My = sum(sum(MF[1::3,1::3]))
    Mr = sum(sum(MF[2::3,2::3]))

    df1_m = pd.DataFrame({'Modo':[],'T(s)':[],'SumUx':[],'SumUy':[],'SumRz':[]})
    
    for j in range(1,Nmodes+1):
        FPx = modo[j-1].T@MF@Ux
        FPy = modo[j-1].T@MF@Uy
        FPr = modo[j-1].T@MF@Rz
        FPRx = FPx**2/Mx
        FPRy = FPy**2/My
        FPRr = FPr**2/Mr
        SUMx = SUMx + FPRx
        SUMy = SUMy + FPRy
        SUMr = SUMr + FPRr
        #
        if min(SUMx,SUMy,SUMr)>=0.90 and ni==0:
            ni = j
        df2_m = pd.DataFrame({'Modo':[j], 'T(s)':[Tmodes[j-1]],'SumUx':[SUMx],'SumUy':[SUMy],'SumRz':[SUMr]})
        df1_m = pd.concat([df1_m, df2_m])
    print(df1_m.round(5))
    print('N° mínimo de Modos a considerar:',ni)
    return ni, modo, Ux, Uy, Rz

def getCombo(E030,MF,modo,Tmodes,NT,ni, Ux, Uy, Rz):

    # Definimos valores iniciales
    D_ABSx,D_RCSCx = np.zeros(NT),np.zeros(NT)
    Δ_ABSx,Δ_RCSCx = np.zeros(NT),np.zeros(NT)
    V_ABSx,V_RCSCx = np.zeros(NT),np.zeros(NT)
    D_ABSy,D_RCSCy = np.zeros(NT),np.zeros(NT)
    Δ_ABSy,Δ_RCSCy = np.zeros(NT),np.zeros(NT)
    V_ABSy,V_RCSCy = np.zeros(NT),np.zeros(NT)

    # Se realiza la Superpocisión Modal Espectral
    for j in range(1,ni+1):#ni+1
        FPx=modo[j-1].T@MF@Ux
        FPy=modo[j-1].T@MF@Uy
        FPr=modo[j-1].T@MF@Rz
        #
        Sa = E030[j-1]*9.80665
        Sd = Sa/(2*np.pi/Tmodes[j-1])**2
        #
        respDX = Sd*FPx*modo[j-1]
        respAX = Sa*FPx*MF@modo[j-1]
        D_ABSx = D_ABSx + abs(respDX)
        D_RCSCx = D_RCSCx + (respDX)**2
        respDX[3:] = respDX[3:] - respDX[:-3]
        Δ_ABSx = Δ_ABSx + abs(respDX)
        Δ_RCSCx = Δ_RCSCx + (respDX)**2
        V_ABSx = V_ABSx + abs(np.cumsum(respAX[::-1])[::-1])
        V_RCSCx = V_RCSCx + (np.cumsum(respAX[::-1])[::-1])**2
        #
        respDY = Sd*FPy*modo[j-1]
        respAY = Sa*FPy*MF@modo[j-1]
        D_ABSy = D_ABSy + abs(respDY)
        D_RCSCy = D_RCSCy + (respDY)**2
        respDY[3:] = respDY[3:] - respDY[:-3]
        Δ_ABSy = Δ_ABSy + abs(respDY)
        Δ_RCSCy = Δ_RCSCy + (respDY)**2
        V_ABSy = V_ABSy + abs(np.cumsum(respAY[::-1])[::-1])
        V_RCSCy = V_RCSCy + (np.cumsum(respAY[::-1])[::-1])**2

    # Se realiza la combinación 25%ABS + 75%RCSC
    D_RCSCx = D_RCSCx**0.5
    Δ_RCSCx = Δ_RCSCx**0.5
    V_RCSCx = V_RCSCx**0.5
    DDx = 0.25*D_ABSx + 0.75*D_RCSCx
    ΔDx = 0.25*Δ_ABSx + 0.75*Δ_RCSCx
    VDx = 0.25*V_ABSx + 0.75*V_RCSCx
    #
    D_RCSCy = D_RCSCy**0.5
    Δ_RCSCy = Δ_RCSCy**0.5
    V_RCSCy = V_RCSCy**0.5
    DDy = 0.25*D_ABSy + 0.75*D_RCSCy
    ΔDy = 0.25*Δ_ABSy + 0.75*Δ_RCSCy
    VDy = 0.25*V_ABSy + 0.75*V_RCSCy

    df_1 = pd.DataFrame({'Nivel':[],'VDx(kN)':[],'VDy(kN)':[],'UDx(cm)':[],'UDy(cm)':[]})
    for i in range(int(NT/3)):
        df_2 = pd.DataFrame({'Nivel':[i+1], 'VDx(kN)':[VDx[0::3][i]/1000],
                        'VDy(kN)':[VDy[1::3][i]/1000],'UDx(cm)':[DDx[0::3][i]*100],
                        'UDy(cm)':[DDy[1::3][i]*100]})
        df_1 = pd.concat([df_1, df_2])

    return DDx, ΔDx, VDx, DDy, ΔDy, VDy, df_1


def AnalisisDinamicoModalEspectral(E030,MF,modo,Tmodes,nz,ni, Ux, Uy, Rz, VS, df_z):
    DDx, ΔDx, VDx, DDy, ΔDy, VDy, df4 = getCombo(E030,MF,modo,Tmodes,3*nz,ni, Ux, Uy, Rz)
    print('\nANÁLISIS DINÁMICO SIN ESCALAR')
    df4 = df4.astype({'Nivel':int})
    print(df4.round(4))

    # Escalamiento de los resultados del análisis dinámico
    if VDx[0::3][0]<0.80*VS[0]:
        FSx  = 0.80*VS[0]/VDx[0::3][0]
        msjx = 'SI es necesario aplicar un Factor de Escala en X: %.4f'%FSx
    else:
        FSx = 1.
        msjx = 'NO es necesario escalar en X'

    if VDy[0::3][0]<0.80*VS[0]:
        FSy  = 0.80*VS[0]/VDy[0::3][0]
        msjy = 'SI es necesario aplicar un Factor de Escala en Y: %.4f'%FSy
    else:
        FSy = 1.
        msjy = 'NO es necesario escalar en Y'

    texto1 = '\nAl comparar la cortante basal obtenida en el análisis dinámico en X \n\
    (%.2f kN) y el 80%% de la cortante basal del análisis estático en X (%.2f kN), \n\
    se obtiene que %s. '%(VDx[0::3][0]/1000,0.80*VS[0]/1000,msjx)
    texto1 = texto1 + '\nEn la dirección Y, la cortante basal obtenida en el análisis \n\
    dinámico es %.2f kN y el 80%% de la cortante basal del análisis estático es %.2f kN. \n\
    Por lo que %s.'%(VDy[0::3][0]/1000,0.80*VS[0]/1000,msjy)
    print(texto1)

    # Se aplican los Factores de Escala
    print('\nANÁLISIS DINÁMICO FINAL')
    Ro = 8.
    df_d1 = pd.DataFrame({'Nivel':[],'Vx(kN)':[],'Vy(kN)':[],'Ux(cm)':[],'Uy(cm)':[],'Δx(‰)':[],'Δy(‰)':[]})
    for i in range(nz):
        Δx = 0.75*Ro*ΔDx[0::3][i]/df_z['Espaciado'].iloc[i]
        Δy = 0.75*Ro*ΔDy[1::3][i]/df_z['Espaciado'].iloc[i]
        #
        df_d2 = pd.DataFrame({'Nivel':[i+1], 'Vx(kN)':[FSx*VDx[0::3][i]/1000],
            'Vy(kN)':[FSy*VDy[1::3][i]/1000],'Ux(cm)':[0.75*Ro*DDx[0::3][i]*100],
            'Uy(cm)':[0.75*Ro*DDy[1::3][i]*100],'Δx(‰)':[Δx*1000],'Δy(‰)':[Δy*1000]})
        df_d1 = pd.concat([df_d1, df_d2])

    df5 = df_d1.astype({'Nivel':int})
    print(df5.round(4))

    # Ploteamos las Distorsiones
    vecX = np.array(df5.loc[:,'Δx(‰)'])
    vecY = np.array(df5.loc[:,'Δy(‰)'])
    lim = 1.1*max(vecX.max(),vecY.max())
    #
    plt.figure()
    plt.plot(np.insert(vecX,0,0),np.arange(nz+1),'bo--',label='drift X',lw = 0.8)
    plt.plot(np.insert(vecY,0,0),np.arange(nz+1),'ro--',label='drift Y',lw = 0.8)
    plt.legend()
    plt.xlabel('Distorsión (‰)')
    plt.ylabel('Nivel')
    #plt.axis([-0.05,lim,-0.05,nz+0.05])
    plt.yticks(np.arange(0, nz+0.05, 1))
    plt.savefig('./distorsion_din.png')