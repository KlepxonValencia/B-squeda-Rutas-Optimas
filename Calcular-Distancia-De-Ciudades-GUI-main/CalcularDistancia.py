import pandas as pd
from tkinter import *
from tkinter.ttk import Treeview, Style
from tkinter import messagebox
import networkx as nx
from Util import VistaTabla
import Util

iconos = ["./iconos/Play.png"]
textoBoton = ["Calcular la distancia"]

def cargar_datos():
    try:
        df = pd.read_csv("ciudades.csv")
        if not set(["Origen", "Destino", "Distancia"]).issubset(df.columns):
            messagebox.showerror("Error", "El archivo CSV debe contener las columnas 'Origen', 'Destino' y 'Distancia'.")
            return None
        return df
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el archivo 'ciudades.csv'.")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", "El archivo 'ciudades.csv' está vacío.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo CSV: {e}")
    return None

def obtenerNombre():
    df = cargar_datos()
    if df is None:
        return []
    ciudades = pd.concat([df["Origen"], df["Destino"]]).drop_duplicates().tolist()
    return [[ciudad] for ciudad in ciudades]

def obtenerNodos():
    df = cargar_datos()
    if df is None:
        return []
    nodos = df[["Origen", "Destino", "Distancia"]].values.tolist()
    return nodos

def ciudades():
    df = cargar_datos()
    if df is None:
        return []
    nombres_ciudades = pd.concat([df["Origen"], df["Destino"]]).drop_duplicates().tolist()
    return nombres_ciudades

def rutaMasCorta(origen, destino):
    df = cargar_datos()
    if df is None:
        return None
    try:
        grafo = nx.from_pandas_edgelist(df, source="Origen", target="Destino", edge_attr="Distancia", create_using=nx.Graph())
        ruta = nx.dijkstra_path(grafo, source=origen, target=destino, weight="Distancia")
    except nx.NetworkXNoPath:
        return None
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al calcular la ruta: {e}")
        return None

    distancias_acumuladas = [[origen, 0]]
    distancia_total = 0

    for i in range(len(ruta) - 1):
        distancia_segmento = grafo[ruta[i]][ruta[i + 1]]['Distancia']
        distancia_total += distancia_segmento
        distancias_acumuladas.append([ruta[i + 1], distancia_total])

    return distancias_acumuladas

def mostrar_distancia():
    origen = ciudad_origen_lista.get()
    destino = ciudad_destino_lista.get()
    
    if destino and not origen:
        messagebox.showwarning("Advertencia", "Por favor selecciona una ciudad de origen para calcular la distancia.")
    elif origen and not destino:
        messagebox.showwarning("Advertencia", "Por favor selecciona una ciudad de destino para calcular la distancia.")
    elif origen and destino:
        recorrido = rutaMasCorta(origen, destino)
        if recorrido is not None:
            tabla_distancia.delete(*tabla_distancia.get_children())
            for item in recorrido:
                tabla_distancia.insert("", "end", values=item)
        else:
            messagebox.showerror("Error", "No se encontró una ruta entre las ciudades seleccionadas.")
    else:
        messagebox.showwarning("Advertencia", "Por favor selecciona ambas ciudades.")

v = Util.crearVentana("Tobby GPS", "800x600")
boton = Util.agregarBarra(v, iconos, textoBoton)
v.iconbitmap("./iconos/icono.ico")


s = Style()
s.configure('Treeview.Heading', font=('Calibri', 12, 'bold'), foreground="#0059b3")
s.configure('Treeview', font=('Calibri', 10), rowheight=25)

main_frame = Frame(v, bg='#f2f7fa')
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

tabla_frame = Frame(main_frame, bg='#f2f7fa')
tabla_frame.pack(side=TOP, fill=X, pady=10)

tabla_nombre_frame = Frame(tabla_frame, bg='#f2f7fa')
tabla_nombre_frame.pack(side=LEFT, fill=BOTH, padx=10)
Label(tabla_nombre_frame, text="Ciudades", bg='#f2f7fa', font=('Arial', 12, 'bold')).pack()
encabezado = ["Nombre"]
nombre = obtenerNombre()
tabla_nombre = Util.mostrarTabla(tabla_nombre_frame, encabezado, nombre)

tabla_nodos_frame = Frame(tabla_frame, bg='#f2f7fa')
tabla_nodos_frame.pack(side=LEFT, fill=BOTH, padx=10)
Label(tabla_nodos_frame, text="Distancias", bg='#f2f7fa', font=('Arial', 12, 'bold')).pack()
encabezado_2 = ["Nodo 1", "Nodo 2", "Valor"]
nodos = obtenerNodos()
tabla_nodos = Util.mostrarTabla(tabla_nodos_frame, encabezado_2, nodos)

seleccion_frame = Frame(main_frame, bg='#f2f7fa')
seleccion_frame.pack(side=TOP, fill=X, pady=10)

origen_frame = Frame(seleccion_frame, bg='#f2f7fa')
origen_frame.pack(side=LEFT, padx=10)
Util.agregarEtiqueta(origen_frame, "Origen", 0, 0)
nombres_ciudades = ciudades()
ciudad_origen_lista = Util.agregarLista(origen_frame, nombres_ciudades, 1, 0)

destino_frame = Frame(seleccion_frame, bg='#f2f7fa')
destino_frame.pack(side=LEFT, padx=10)
Util.agregarEtiqueta(destino_frame, "Destino", 0, 0)
ciudad_destino_lista = Util.agregarLista(destino_frame, nombres_ciudades, 1, 0)

recorrido_frame = Frame(seleccion_frame, bg='#f2f7fa')
recorrido_frame.pack(side=LEFT, fill=X, padx=10)
Label(recorrido_frame, text="Recorrido", bg='#f2f7fa', font=('Arial', 12, 'bold')).pack()

scroll_y = Scrollbar(recorrido_frame, orient=VERTICAL)
scroll_x = Scrollbar(recorrido_frame, orient=HORIZONTAL)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_x.pack(side=BOTTOM, fill=X)

encabezado_recorrido = ["Nombre", "Valor"]
recorrido_data = []
tabla_distancia = Treeview(recorrido_frame, columns=encabezado_recorrido, show="headings", xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
scroll_x.config(command=tabla_distancia.xview)
scroll_y.config(command=tabla_distancia.yview)

for col in encabezado_recorrido:
    tabla_distancia.heading(col, text=col)
    tabla_distancia.column(col, minwidth=100, width=150, stretch=True)

tabla_distancia.pack(fill=BOTH, expand=True)

boton[0].config(command=lambda: mostrar_distancia())

v.mainloop()
