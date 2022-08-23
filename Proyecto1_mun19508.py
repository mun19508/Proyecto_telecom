# Autor: Daniel Mundo
# Carnet: 19508
# Curso: Sistemas de Telecomunicaciones 1
# Seccion: 10
from turtle import color
from xml.dom.minicompat import NodeList
import requests
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
from Interfaz_main import Ui_Dialog
from PyQt6 import QtWidgets

global ip, AS_end, initial_time, end_time
''' ------------------------------------------------------------------------
                    Apartado de interfaz grafica                          
------------------------------------------------------------------------'''
class Ventana(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Funciones que se realizan depediedno del boton presionado
        self.ButtonRisp.clicked.connect(self.PlotRISP)
        self.ButtonBGP.clicked.connect(self.PlotBGP)
    # -------------------------------------------------------------------------------------------
    '''Funcion en la cual se grafica la informacion obtenida de ris-peering'''

    def PlotRISP(self):
        ip = self.IP_Input.text()  # Se obtiene la IP destino
        # __________________________________________________________________________________
        # Rutina empleada para obtener la informacion del AS destino
        AS_end_str = self.AS_Input.text()
        if AS_end_str != '':
            AS_end = int(AS_end_str)
        else:
            AS_end = []
        # __________________________________________________________________________________
        initial_time = '{}T{}'.format(self.dateStart_Input.text(), self.timeStart_Input.text())
        
        end_time = '{}T{}'.format(self.dateEnd_Input.text(), self.timeEnd_Input.text())
        # __________________________________________________________________________________
        AS_Path_BGPI, AS_Path_BGPE = RIPE_BGPlay(ip, initial_time, end_time)  # Rutas de los AS
        AS_path0_bgp = Path_Generator(AS_Path_BGPI, AS_end)
       
        # __________________________________________________________________________________
        # Rutina para la obtencion de el cambio de rutas de AS:
       
        # Propagacion de anuncios (inicio)
        AS_PairList_BGI = Pair_Generator(AS_Path_BGPI)
        # __________________________________________________________________________________
        BGP_Node = AS_Path_BGPI
        AS_BGP_NodeList = Node_Generator(BGP_Node)  # Nodos sin los de interes
        for element in AS_path0_bgp:
            AS_BGP_NodeList.remove(element)
        try:
            AS_BGP_NodeList.remove(AS_Path_BGPI[0][-1])
        except:
            pass
        # __________________________________________________________________________________
        PlotASNRISP(AS_PairList_BGI, AS_BGP_NodeList, AS_path0_bgp,  AS_Path_BGPI[0][-1], AS_end)
    # --------------------------------------------------------------------------------------
    '''Funcion en la cual se grafica la informacion obtenida de bgplay'''

    def PlotBGP(self):
        ip = self.IP_Input.text()  # Se obtiene la IP destino
        # __________________________________________________________________________________
        # Rutina empleada para obtener la informacion del AS destino
        AS_end_str = self.AS_Input.text()
        if AS_end_str != '':
            AS_end = int(AS_end_str)
        else:
            AS_end = []
        # __________________________________________________________________________________
        initial_time = '{}T{}'.format(self.dateStart_Input.text(), self.timeStart_Input.text())
        
        end_time = '{}T{}'.format(self.dateEnd_Input.text(), self.timeEnd_Input.text())
        # __________________________________________________________________________________
        AS_Path_BGPI, AS_Path_BGPE = RIPE_BGPlay(ip, initial_time, end_time)  # Rutas de los AS
        AS_path0_bgp = Path_Generator(AS_Path_BGPI, AS_end)
       
        # __________________________________________________________________________________
        # Rutina para la obtencion de el cambio de rutas de AS:
        AS_notchange = []
        AS_PairList_BGE= []
        ''' Se compara todas las rutas nuevas con las rutas viejas se almacenara primero
            los valores en las cuales estas coinciden y posteriormente esta se eliminaran
            para que unicamente esten las rutas que hayan cambiado'''
        for n in range(len(AS_Path_BGPE)-1):
            for element in AS_Path_BGPI[n]:
                if element == AS_Path_BGPE[n]:
                    AS_notchange.append(AS_Path_BGPE[n])
        try:
            AS_change= AS_Path_BGPE
            for element in AS_notchange:
                AS_change.remove(element)
        except:
            pass
        # Propagacion de anuncios (inicio)
        AS_PairList_BGI = Pair_Generator(AS_Path_BGPI)
        ''' Se asegura que unicamente se muestre el reanuncio 1 vez'''
        AS_PairListAux_BGE = Pair_Generator(AS_change)  # Cambios en la propagacion
        for element in AS_PairListAux_BGE:
            if element not in AS_PairList_BGE and element not in AS_PairList_BGI:
                AS_PairList_BGE.append(element) # reanuncios globales
        # __________________________________________________________________________________
        BGP_Node = AS_Path_BGPI+AS_Path_BGPE
        AS_BGP_NodeList = Node_Generator(BGP_Node)  # Nodos sin los de interes
        for element in AS_path0_bgp:
            AS_BGP_NodeList.remove(element)
        try:
            AS_BGP_NodeList.remove(AS_Path_BGPI[0][-1])
        except:
            pass
        # __________________________________________________________________________________
        PlotASNBGP(AS_PairList_BGI, AS_PairList_BGE,
                   AS_BGP_NodeList, AS_path0_bgp, AS_Path_BGPI[0][-1], AS_end)
''' ------------------------------------------------------------------------
                        Apartado de Funciones                          
------------------------------------------------------------------------'''
# --------------------Funcion empleada para graficar----------------------

def PlotASNBGP(ASN_Connect_initial, ASN_Connect_end, ASN_Node, ASN_Path0, ASN_source, ASN_dest):
    # ASN_Connect_initial: corresponde a las conexiones originales
    # ASN_Connect_initial: corresponde a las conexiones que cambiaron
    # ASN_Node: corresponde a todos los nodos que no son parte de Path0
    # ASN_Path0: corresponde a todos los nodos que son parte del camino de propagacion
    #________________________________________________________________________________
    net = Network(directed=True, height="700px",
                  width='1500px')  # Se genera la gráfica
    net.add_nodes(ASN_Node, label=[str(x)
                  for x in ASN_Node])  # Se agregan los nodos
    #________________________________________________________________________________
    ''' Se comprueba si  la variable ASN_Path0 es una lista vacia, si no lo es
        Se remueven de la misma el AS origen y el As de destino y se agregan dichos 
        nodos con color rojo'''
    try:
        if ASN_Path0 != []:
            ASN_Path0.remove(ASN_source)
            ASN_Path0.remove(ASN_dest)
            net.add_node(ASN_dest, str(ASN_dest), color='#2d572c')
            for element in ASN_Path0:
                net.add_node(element, str(element), color='#eb4034')
    except:
        pass
    #________________________________________________________________________________
    net.add_node(ASN_source, str(ASN_source), color='#65eb34')
    #________________________________________________________________________________
    net.add_edges(ASN_Connect_initial)  # Se agregan las relaciones entre nodos
    for i in range(len(ASN_Connect_end)-1):
        net.add_edge(
            ASN_Connect_end[i][0], ASN_Connect_end[i][1], title="Reanuncio", value=1.5)
        # Se agregan las relaciones entre nodos
    net.show('BGplay.html')  # Se muestra la gráfica final
    return

def PlotASNRISP(ASN_Connect, ASN_Label, ASN_Path, ASN_source, ASN_dest):
    # ASN_Connect: corresponde a las conexiones
    # ASN_Label: corresponde a todos los nodos que no son parte de Path
    # ASN_Path: corresponde a todos los nodos que son parte del camino de propagacion
    net = Network(directed=True, height="700px",
                  width='1500px')  # Se genera la gráfica
    net.add_nodes(ASN_Label, label=[str(x)
                  for x in ASN_Label])  # Se agregan los nodos
    ''' Se comprueba si  la variable ASN_Path es una lista vacia, si no lo es
        Se remueven de la misma el AS origen y el As de destino y se agregan dichos nodos
        con color rojo'''
    try:
        if ASN_Path != []:
            ASN_Path.remove(ASN_source)
            ASN_Path.remove(ASN_dest)
            net.add_node(ASN_dest, str(ASN_dest), color='#2d572c')
            for element in ASN_Path:
                net.add_node(element, str(element), color='#eb4034')
    except:
        pass
    #net.add_node(ASN_dest, str(ASN_dest), color='#ff8800')
    net.add_node(ASN_source, str(ASN_source), color='#65eb34')
    net.add_edges(ASN_Connect)  # Se agregan las relaciones entre nodos
    net.show('Ris_peering.html')  # Se muestra la gráfica final
    return
# --------------Funcion empleada para realizar las solicitudes--------------------

def RIPE_RIS_peerings(ip):
    # Se genera el link de consulta
    url = 'https://stat.ripe.net/data/ris-peerings/data.json?resource={}'.format(
        ip)
    resp = requests.get(url)
    # Formato para la adquision de la informacion:
    # ['data']['peerings'][0]['peers'][0]['routes'][0]['as_path']=
    # data
    #   peerings
    #       0
    #           peers
    #               0
    #                   routes
    #                       0
    #                           as_path
    # Encuentra la cantidad total de peerings:
    No_peering = len(resp.json()['data']['peerings'])
    AuxList = []
    # Se incia la rutina para la extracción de información
    for i in range(No_peering):
        # Encuentra la cantida de peers para el n-esimo peering:
        No_peers = len(resp.json()['data']['peerings']
                       [i]['peers'])
        for j in range(No_peers):
            try:
                AuxList.append(
                    resp.json()['data']['peerings'][i]['peers'][j]['routes'][0]['as_path'])
            except:
                pass
    return AuxList
# --------------Funcion empleada para realizar las solicitudes--------------------


def RIPE_BGPlay(ip, initial, end):
    # Se genera el link de consulta
    url = 'https://stat.ripe.net/data/bgplay/data.json?resource={}&starttime={}&endtime={}'.format(
        ip, initial, end)
    resp = requests.get(url)
    # Obtencion de la informacion en Initial State
    No_initial_state = len(resp.json()['data']['initial_state'])
    IS_List = []
    # Se incia la rutina para la extracción de información
    for i in range(No_initial_state):
    # Encuentra la cantida de peers para el n-esimo peering:
        try:
            IS_List.append(resp.json()['data']['initial_state'][i]['path'])
        except:
            pass
    # Obtencion de la informacion en Event
    No_event = len(resp.json()['data']['events'])
    E_List = []
    for i in range(No_event):
    # Encuentra la cantida de peers para el n-esimo peering:
        try:
            E_List.append(resp.json()['data']['events'][i]['attrs']['path'])
        except:
            pass
    return IS_List, E_List
# --------------Funcion empleada para generar los nodos del Grafo--------------------

def Node_Generator(AuxList):
    Nlist = []
    # Se genera la lista para los nodos
    for i in range(len(AuxList)-1):
        for element in AuxList[i]:
            if element not in Nlist:
                Nlist.append(element)
    return Nlist
# -------------Funcion empleada para generar las aristas del Grafo-------------------

def Pair_Generator(AuxList):
    # Se genera la lista para la obtencion de la relación entre nodos
    PairList = []
    Aux2 = []
    for i in range(len(AuxList)-1):
        for j in range(len(AuxList[i])-1):
            PairList.append((AuxList[i][j+1], AuxList[i][j]))
    for element in PairList:
        if element not in Aux2:
            Aux2.append(element)
    return Aux2

def Path_Generator(List_ASN, dest):
    # Rutina para la obtencion de la ruta hacia el AS de interes:
    Aux = []
    for i in range(len(List_ASN)-1):
        try:
            if List_ASN[i][0] ==dest:
                print(List_ASN[i])
            k= List_ASN[i].index(dest)
            for j in range(len(List_ASN[i])-k):
                if List_ASN[i][j+k] not in Aux:
                    Aux.append(List_ASN[i][j+k])
        except:
            pass
    return Aux
# ------------------------------------------------------------------------
#                                 Main                                  -
# ------------------------------------------------------------------------
app = QtWidgets.QApplication([])
ventana = Ventana()
ventana.show()
app.exec()