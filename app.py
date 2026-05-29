from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import os, csv, io
from io import StringIO
from collections import defaultdict
import datetime
import time
from zoneinfo import ZoneInfo
import pandas as pd
import re


app = Flask(__name__)
app.secret_key = "cambiar_esta_clave_por_una_segura"

# Configuración Azure Blob
connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = None
container_name = "pedidos"
blob_name = "pedidos.csv"

connection_string = "DefaultEndpointsProtocol=https;AccountName=rpastorageaccountrpa;AccountKey=eF8T2q0lWtwV8koJgkg6UXaVPMEGSsRgnp6//WbQ1mEnpAL72EJjM+lJdfE+sD+axPOOq1jZOm07arpk11BWng==;EndpointSuffix=core.windows.net"
if connection_string:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)


# Productos disponibles (id, nombre, precio, imagen en static/img)
productos = [
    {"id": 1, "nombre": "Bolivia", "precio": 2.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 2, "nombre": "Portete", "precio": 3.00, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 3, "nombre": "Goyena", "precio": 3.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 4, "nombre": "Guayaka", "precio": 3.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 5, "nombre": "La 21", "precio": 4.00, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 43, "nombre": "El Oro (Pollo)", "precio": 3.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 50, "nombre": "Vacas Galindo", "precio": 3.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},

    {"id": 51, "nombre": "Porción Papas", "precio": 1.00, "imagen": "papas.png", "tipo": "papas"},
    {"id": 52, "nombre": "Salchipapa", "precio": 1.50, "imagen": "salchi.png", "tipo": "papas"},
    {"id": 53, "nombre": "Papas Pulled Pork", "precio": 2.50, "imagen": "papaspulled.png", "tipo": "papas"},
    {"id": 54, "nombre": "Papas Chilli Chesse", "precio": 2.50, "imagen": "papaschesse.png", "tipo": "papas"},
    {"id": 19, "nombre": "Papipollo", "precio": 3.00, "imagen": "papipollo.png", "tipo": "papas"},
    {"id": 55, "nombre": "Choripan (Del Astillero)", "precio": 2.25, "imagen": "choripan.png", "tipo": "papas"},
    {"id": 56, "nombre": "Hot Dog (Sin Verguenza - chilli chesse)", "precio": 2.00, "imagen": "hotdogchilli.png", "tipo": "papas"},
    {"id": 57, "nombre": "Hot Dog (Sencillo)", "precio": 1.50, "imagen": "hotdog.png", "tipo": "papas"},

    {"id": 6, "nombre": "Ñengosa (carne)", "precio": 2.50, "imagen": "bandeja3.png", "tipo": "Bandejitas"},
    {"id": 7, "nombre": "Pelucona (Pollo)", "precio": 2.50, "imagen": "bandeja3.png", "tipo": "Bandejitas"},
    {"id": 8, "nombre": "Cholaza (Chorizo)", "precio": 2.50, "imagen": "bandeja3.png", "tipo": "Bandejitas"},
    {"id": 9, "nombre": "Fulleteada (Mixta)", "precio": 3.00, "imagen": "bandeja3.png", "tipo": "Bandejitas"},
    #{"id": 10, "nombre": "PolloChampi", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    #{"id": 11, "nombre": "Tocinetona", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    #{"id": 12, "nombre": "Hawaiaca", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},


    {"id": 13, "nombre": "Carne", "precio": 4.50, "imagen": "lasaña.png", "tipo": "Lasaña"},
    {"id": 14, "nombre": "Pollo", "precio": 4.50, "imagen": "lasaña.png", "tipo": "Lasaña"},
    {"id": 15, "nombre": "Mixto", "precio": 5.00, "imagen": "lasaña.png", "tipo": "Lasaña"},

    {"id": 16, "nombre": "Carne", "precio": 1.50, "imagen": "dori.png", "tipo": "Doriloco"},
    {"id": 17, "nombre": "Pollo", "precio": 1.75, "imagen": "dori.png", "tipo": "Doriloco"},
    {"id": 18, "nombre": "Mixto", "precio": 2.00, "imagen": "dori.png", "tipo": "Doriloco"},
    {"id": 37, "nombre": "Carne", "precio": 1.50, "imagen": "ruffles.png", "tipo": "Doriloco"},
    {"id": 38, "nombre": "Pollo", "precio": 1.75, "imagen": "ruffles.png", "tipo": "Doriloco"},
    {"id": 39, "nombre": "Mixto", "precio": 2.00, "imagen": "ruffles.png", "tipo": "Doriloco"},
    {"id": 40, "nombre": "Carne", "precio": 2.50, "imagen": "rapidito.png", "tipo": "Doriloco"},
    {"id": 41, "nombre": "Pollo", "precio": 2.50, "imagen": "rapidito.png", "tipo": "Doriloco"},
    #{"id": 42, "nombre": "Mixto", "precio": 2.50, "imagen": "rapidito.png", "tipo": "Doriloco"},
    
    #{"id": 20, "nombre": "Salchipapa", "precio": 1.50, "imagen": "salchi.png", "tipo": "Adicional"},
    {"id": 21, "nombre": "Tocino", "precio": 0.75, "imagen": "tocino.png", "tipo": "Adicional"},
    {"id": 22, "nombre": "Salchicha", "precio": 0.75, "imagen": "salchicha.png", "tipo": "Adicional"},
    {"id": 23, "nombre": "Cheddar", "precio": 0.50, "imagen": "cheddar.png", "tipo": "Adicional"},
    {"id": 24, "nombre": "Piña", "precio": 0.25, "imagen": "piña.png", "tipo": "Adicional"},
    {"id": 25, "nombre": "Huevo", "precio": 0.50, "imagen": "huevo.png", "tipo": "Adicional"},
    #{"id": 44, "nombre": "Papas", "precio": 1.00, "imagen": "papas.png", "tipo": "Adicional"},
    {"id": 45, "nombre": "Carne", "precio": 0.50, "imagen": "carne.png", "tipo": "Adicional"},
    {"id": 46, "nombre": "Pollo", "precio": 0.50, "imagen": "pollo.png", "tipo": "Adicional"},
    #{"id": 47, "nombre": "Pulled Pork", "precio": 0.50, "imagen": "pork.png", "tipo": "Adicional"},

    
    {"id": 27, "nombre": "Coca Cola Ori", "precio": 0.60, "imagen": "cola.png", "tipo": "Bebida"},
    {"id": 28, "nombre": "Fioravanti", "precio": 0.50, "imagen": "fiora.png", "tipo": "Bebida"},
    {"id": 29, "nombre": "Fanta", "precio": 0.50, "imagen": "fanta.png", "tipo": "Bebida"},
    {"id": 48, "nombre": "Sprite", "precio": 0.50, "imagen": "sprite.png", "tipo": "Bebida"},
    {"id": 62, "nombre": "Coca Cola Zero (500ml)", "precio": 0.75, "imagen": "cola.png", "tipo": "Bebida"},
    {"id": 61, "nombre": "Inca Cola", "precio": 0.50, "imagen": "inca.png", "tipo": "Bebida"},
    {"id": 58, "nombre": "Jugo Mora", "precio": 0.75, "imagen": "mora.png", "tipo": "Bebida"},
    {"id": 59, "nombre": "Jugo Frutilla", "precio": 0.75, "imagen": "frutilla.png", "tipo": "Bebida"},
    {"id": 60, "nombre": "Fuze Tea (550ml)", "precio": 0.75, "imagen": "fuzetea.png", "tipo": "Bebida"},


    {"id": 30, "nombre": "Jamón", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 31, "nombre": "Peperoni", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 32, "nombre": "Salami", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 33, "nombre": "Carne", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 34, "nombre": "Pollo", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    #{"id": 35, "nombre": "Tocinetona", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 36, "nombre": "Hawaiana", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 49, "nombre": "Personalizada", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"}
]

pedidos = {}  # {pedido_id: [ {nombre, precio, imagen, eliminado?}, ... ] }
pedido_counter = 1
archivo = "pedidos.csv"


@app.route("/")
def index():
    # Calcular total general ignorando los eliminados
    total_general = sum(
    sum(item["precio"] for item in items)
     for items in pedidos.values()
)


    return render_template("index.html", productos=productos, pedidos=pedidos, total_general=total_general)


def leer_csv_blob():
    """
    Descarga el CSV desde Azure Blob Storage y lo retorna como DataFrame de pandas
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # Descargar contenido
        blob_data = blob_client.download_blob().content_as_text()

        # Cargar en pandas
        # df = pd.read_csv(StringIO(blob_data))
        df = pd.read_csv(StringIO(blob_data), sep=";")

        return df
    except Exception as e:
        print("Error leyendo CSV desde Azure:", e)
        return pd.DataFrame()  # dataframe vacío si falla



@app.route("/resumen_diario", methods=["GET"])
def resumen_diario():
    df = leer_csv_blob()
    if df.empty:
        return jsonify({"ventas_totales": 0, "productos_vendidos": 0, "detalle": []})

    # Convertir FECHA a datetime
    df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d-%m-%Y", errors="coerce")

    df["PRECIO"] = (
        df["PRECIO"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(\d+\.?\d*)")[0]
    )

    #df["PRECIO"] = pd.to_numeric(df["PRECIO"], errors="coerce")



    # --- Manejo de fecha ---
    fecha_param = request.args.get("fecha")  # YYYY-MM-DD desde JS
    if fecha_param:
        try:
            fecha_consulta = datetime.datetime.strptime(fecha_param, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}), 400
    else:
        # Si no viene parámetro, usar fecha actual de Ecuador
        now = datetime.datetime.now(ZoneInfo("America/Guayaquil"))
        fecha_consulta = now.date()



    #now = datetime.datetime.now(ZoneInfo("America/Guayaquil"))
    #hoy = now.date()
    #hoy = now.strftime("%d-%m-%Y")
    #hoy = datetime.datetime.now().date()

    # Filtrar por fecha actual
    #df_hoy = df[df["FECHA"].dt.date == hoy]
    df_hoy = df[df["FECHA"].dt.date == fecha_consulta]

    #print(df["FECHA"].dt.date)
    #print(hoy)
    #print(df["PRECIO"])

    if df_hoy.empty:
        return jsonify({
            "ventas_totales": 0,
            "productos_vendidos": 0,
            "detalle": [],
            "fecha": fecha_consulta.strftime("%d-%m-%Y")
            
        })
    
    #df_hoy.loc[:, "PRECIO"] = df_hoy["PRECIO"].astype(float)
    df_hoy.loc[:, "PRECIO"] = df_hoy["PRECIO"].apply(limpiar_precios)


    # Calcular totales
    ventas_totales = df_hoy["PRECIO"].sum(skipna=True)
    #print(ventas_totales)
        
    productos_vendidos = len(df_hoy)

    detalle = (
        df_hoy.groupby(["TIPO_PRODUCTO", "NOMBRE_PRODUCTO"])
        .agg(
            cantidad=("NOMBRE_PRODUCTO", "count"),
            precio=("PRECIO", "sum")
        )
        .reset_index()
    )

    # convertir a lista de dicts
    detalle_list = []
    for _, row in detalle.iterrows():
        detalle_list.append({
            "tipo": row["TIPO_PRODUCTO"],
            "nombre": row["NOMBRE_PRODUCTO"],
            "cantidad": int(row["cantidad"]),
            "precio": float(row["precio"])
        })

    return {
        "ventas_totales": float(ventas_totales),
        "productos_vendidos": int(productos_vendidos),
        "detalle": detalle_list
    }



def limpiar_precios(x):
    # Extraer todos los números de la cadena y sumarlos
    numeros = [float(n) for n in re.findall(r'\d+\.?\d*', str(x))]
    return sum(numeros)





@app.route("/agregar/<int:producto_id>")
def agregar(producto_id):
    global pedido_counter

    # Si no hay pedidos, crear el primero
    if not pedidos:
        pedidos[str(pedido_counter)] = []

    # Buscar el producto
    producto = next((p for p in productos if p["id"] == producto_id), None)
    if producto:
        # Tomar el último pedido abierto
        pedido_id = list(pedidos.keys())[-1]
        pedidos[pedido_id].append({
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "imagen": producto["imagen"],
            "tipo": producto["tipo"],
            "eliminado": False
        })

    #fecha = datetime.now().strftime("%d/%m/%Y")
    #fecha2 = datetime.now().strftime("%H:%M:%S")
    fecha = time.strftime("%Y-%m-%d")
    fecha2 = time.strftime("%H:%M:%S")
    
    with open(archivo, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([fecha, fecha2, producto["id"], producto["tipo"], producto["nombre"], producto["precio"], False])
    
    return redirect(url_for("index"))



@app.route("/nuevo_pedido")
def nuevo_pedido():
    global pedido_counter, pedidos
    pedido_counter += 1
    pedidos[pedido_counter] = []  # Nuevo pedido vacío
    return redirect(url_for("index"))


@app.route("/eliminar/<pedido_id>/<int:indice>")
def eliminar(pedido_id, indice):
    """Marcar un item como eliminado (deshabilitado)"""
    if pedido_id in pedidos and 0 <= indice < len(pedidos[pedido_id]):
        pedidos[pedido_id][indice]["eliminado"] = True
    return redirect(url_for("index"))


@app.route("/eliminar_pedido", methods=["POST"])
def eliminar_pedido():
    global pedidos
    data = request.get_json()
    pedido_id = data.get("pedido_id")

    try:
        pedido_id = int(pedido_id)
    except (TypeError, ValueError):
        return jsonify({"error": "ID de pedido inválido"}), 400

    if pedido_id in pedidos:
        del pedidos[pedido_id]

    return jsonify(generar_respuesta_carrito())



##@app.route("/cerrar_pedido/<pedido_id>")
##def cerrar_pedido(pedido_id):
##    """Eliminar por completo un pedido"""
##    if pedido_id in pedidos:
##        del pedidos[pedido_id]
##    return redirect(url_for("index"))






@app.route("/cerrar_pedidos")
def cerrar_pedidos():
    """Vaciar todos los pedidos"""
    global pedidos
    pedidos.clear()
    return redirect(url_for("index"))


@app.route('/vaciar')
def vaciar():
    session['carrito'] = []
    return redirect(url_for('index'))


@app.route("/reactivar/<pedido_id>/<int:indice>")
def reactivar(pedido_id, indice):
    """Reactivar un item que estaba marcado como eliminado"""
    if pedido_id in pedidos and 0 <= indice < len(pedidos[pedido_id]):
        pedidos[pedido_id][indice]["eliminado"] = False
    return redirect(url_for("index"))



@app.route("/eliminar_ajax", methods=["POST"])
def eliminar_ajax():
    data = request.get_json()
    try:
        pedido_id = int(data.get("pedido_id"))
        indice = int(data.get("indice"))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if pedido_id not in pedidos or indice < 0 or indice >= len(pedidos[pedido_id]):
        return jsonify({"error": "Producto no encontrado"}), 404

    # 🔹 Solo marcar como eliminado, no quitar del total
    #pedidos[pedido_id][indice]["eliminado"] = True

    pedidos[pedido_id].pop(indice)

    
    return jsonify(generar_respuesta_carrito(contar_eliminados=True))



@app.route("/agregar_ajax", methods=["POST"])
def agregar_ajax():
    global pedidos, pedido_counter

    data = request.get_json()

    try:
        producto_id = int(data.get("producto_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "ID de producto inválido"}), 400

    tamano = data.get("tamano")
    sabores = data.get("sabores", [])
    pedido_id = data.get("pedido_id")

    # Buscar producto
    producto = next((p for p in productos if p["id"] == producto_id), None)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    # Ajustar precio si es pizza
    precio_final = producto["precio"]
    if producto["tipo"] == "Pizza Entera" and tamano:
        if tamano == "Pequeña":
            precio_final = 4.50
        elif tamano == "Mediana":
            precio_final = 6.00
        elif tamano == "Grande":
            precio_final = 10.50
        elif tamano == "Personal":
            precio_final = 2.25

    if producto["tipo"] == "Adicional" and producto["id"]==19 and tamano:
        if tamano == "Pechuga":
            precio_final = 3.00
        elif tamano == "Cadera":
            precio_final = 3.00
        elif tamano == "Ala":
            precio_final = 2.50
        elif tamano == "Pierna":
            precio_final = 2.50

    if producto["tipo"] == "Bebida" and (producto["id"]==28 or producto["id"]==29 or producto["id"]==48) and tamano:
        if tamano == "300ml":
            precio_final = 0.50
        elif tamano == "500ml":
            precio_final = 0.75

    if producto["tipo"] == "Bebida" and (producto["id"]==27) and tamano:
        if tamano == "300ml":
            precio_final = 0.50
        elif tamano == "500ml":
            precio_final = 1.00
        
    #28Fiora,29fanta,48sprite

    #global pedidos, pedido_counter


   # 📌 Determinar a qué pedido agregar
    if pedido_id is not None:
        try:
            pedido_id = int(pedido_id)
        except ValueError:
            return jsonify({"error": "ID de pedido inválido"}), 400

        # Si no existe, lo creamos
        if pedido_id not in pedidos:
            pedidos[pedido_id] = []
    else:
        # Si no hay pedidos, creamos el primero
        if not pedidos:
            pedidos[pedido_counter] = []
            pedido_id = pedido_counter
            pedido_counter += 1
        else:
            pedido_id = max(pedidos.keys())

    # Si el pedido está marcado como cerrado, no permitir agregar
    if pedidos[pedido_id] and pedidos[pedido_id][-1].get("cerrado"):
        return jsonify({"error": "Este pedido está cerrado"}), 400

    # Construir nombre con sabores (si aplica)
    if sabores:
        sabores_texto = "Sabores:<br>" + "<br>".join(f"• {s}" for s in sabores)
        nombre_completo = f"{producto['nombre']}{f' ({tamano})' if tamano else ''}<br>{sabores_texto}"
    else:
        nombre_completo = f"{producto['nombre']}{f' ({tamano})' if tamano else ''}"

    # Crear ítem
    nuevo_item = {
        "nombre": nombre_completo,
        "precio": precio_final,
        "imagen": producto["imagen"],
        "tipo": producto["tipo"]
    }

    # Agregar producto al pedido correcto
    pedidos[pedido_id].append(nuevo_item)

    return jsonify(generar_respuesta_carrito())




def guardar_pedido_en_blob(pedido_id, pedido_items, tamano):

    #fecha_hora = time.strftime("%d/%m/%Y %H:%M")
    # 📌 Fecha y hora con time.strftime()
    
    now = datetime.datetime.now(ZoneInfo("America/Guayaquil"))

    
    fecha = now.strftime("%d-%m-%Y")
    hora = now.strftime("%H:%M:%S")
    
    nombre_archivo = "pedidos.csv"

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    
    #writer.writerow(["Fecha", "Hora", "PedidoID", "Tipo", "Producto", "Precio", "Tamano"])
    contenido_actual = ""
    contenido_final = ""
    
    if blob_service_client:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        try:
            contenido_actual = blob_client.download_blob().readall().decode("utf-8")
            output.write(contenido_actual)
        except Exception:
            # Si no existe, escribir encabezado
            writer.writerow(["Fecha", "Hora", "PedidoID", "Tipo", "Producto", "Precio", "Tamano"])


    total_pedido = sum(item["precio"] for item in pedido_items if not item.get("eliminado", False))
    
    for item in pedido_items:
        if not item.get("eliminado", False):
            nombre_final = item["nombre"]
            #if item.get("tamano"):
            #    tamano = tamano
            #else:
            #    tamano= "N/A"
            writer.writerow([fecha, hora, pedido_id, item["tipo"], nombre_final, item["precio"], tamano])
            #output.write([fecha, hora, producto["id"], producto["tipo"], producto["nombre"], producto["precio"], tamano if tamano else "N/A"])

    # Ir al inicio antes de subir
    contenido_final = output.getvalue()

    # Subir el CSV actualizado a Blob Storage
    if blob_service_client:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(contenido_final, overwrite=True)
        print(f"Pedido {pedido_id} guardado en Azure Blob Storage ({blob_name})")
    else:
        # Guardado local si no hay conexión a Azure
        with open(blob_name, "w", newline="", encoding="utf-8") as f:
            f.write(contenido_final)
        print(f"💾 Pedido {pedido_id} guardado localmente en {blob_name}")
        
##        with open(nombre_archivo, mode="a", newline="", encoding="utf-8") as file:
##            local_writer = csv.writer(file, delimiter=";")
##            if os.stat(nombre_archivo).st_size == 0:
##                #local_writer.writerow(["FechaHora", "PedidoID", "Producto", "Precio", "Total", "PagoCliente", "Vuelto"])
##                file.write(contenido_final)
##        print(f"Pedido {pedido_id} guardado en local ({archivo_csv})")

    



def generar_respuesta_carrito(contar_eliminados=False):
    pedidos_data = []
    total_general = 0
    for pid, items in pedidos.items():
        if contar_eliminados:
            total_pedido = sum(item["precio"] for item in items if "cerrado" not in item)
        else:
            total_pedido = sum(item["precio"] for item in items if not item.get("eliminado", False) and "cerrado" not in item)

        total_general += total_pedido
        pedidos_data.append({
            "id": pid,
            "items": items,
            "total": total_pedido
        })
    return {"carrito": pedidos_data, "total_general": total_general}



@app.route("/cerrar_y_cobrar", methods=["POST"])
def cerrar_y_cobrar():
    data = request.get_json()
    try:
        pedido_id = int(data.get("pedido_id"))
        #tipo = data.get("tipo")
        tamano = "" #str(data.get("tamano"))
        pago_cliente = float(data.get("pago_cliente"))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if pedido_id not in pedidos:
        return jsonify({"error": "Pedido no encontrado"}), 404

    # Calcular total del pedido
    total_pedido = sum(item["precio"] for item in pedidos[pedido_id])
    vuelto = pago_cliente - total_pedido

    guardar_pedido_en_blob(pedido_id, pedidos[pedido_id], tamano)


    # Eliminar pedido de la memoria después de cobrar
    #pedidos[pedido_id] = []
    
    del pedidos[pedido_id]

    #return jsonify({"success": True, "vuelto": vuelto, "carrito": generar_respuesta_carrito(contar_eliminados=True), "pedidos": pedidos})
    #return jsonify(generar_respuesta_carrito())
    respuesta = generar_respuesta_carrito()
    respuesta["vuelto"] = vuelto
    return jsonify(respuesta)


@app.route("/cerrar_pedido", methods=["POST"])
def cerrar_pedido():
    data = request.get_json()
    try:
        pedido_id = int(data.get("pedido_id"))
        pago_cliente = float(data.get("pago_cliente"))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if pedido_id not in pedidos:
        return jsonify({"error": "Pedido no encontrado"}), 404

    total_pedido = sum(item["precio"] for item in pedidos[pedido_id])
    vuelto = pago_cliente - total_pedido

    # Eliminar el pedido del diccionario
    del pedidos[pedido_id]

    return jsonify({
        "pedido_id": pedido_id,
        "total": total_pedido,
        "vuelto": vuelto,
        "carrito": generar_respuesta_carrito()["carrito"],
        "total_general": generar_respuesta_carrito()["total_general"]
    })



# Modificar producto de un pedido
@app.route("/modificar_item", methods=["POST"])
def modificar_item():
    data = request.get_json()
    pedido_id = int(data.get("pedido_id"))
    item_index = int(data.get("item_index"))
    tamano = data.get("tamano")
    sabores = data.get("sabores", [])

    if pedido_id not in pedidos or item_index >= len(pedidos[pedido_id]):
        return jsonify({"error": "Pedido o producto no encontrado"}), 400

    # Actualizar en memoria
    item = pedidos[pedido_id][item_index]
    item["tamano"] = tamano
    item["sabores"] = sabores

    # Si quieres actualizar el nombre visible
    if sabores:
        sabores_texto = "\n".join(f"• {s}" for s in sabores)
        item["nombre"] = f"{item['nombre'].split(' (')[0]} ({tamano})\n{sabores_texto}"
    else:
        item["nombre"] = f"{item['nombre'].split(' (')[0]} ({tamano})"

    # Si cambia el precio
    item["precio"] = calcular_precio(item["nombre"], tamano)

    return jsonify({"success": True, "pedidos": pedidos})






if __name__ == "__main__":
    from waitress import serve
    import os
    port = int(os.environ.get("PORT", 5001))
    print(f"--> Servidor iniciado en http://localhost:{port}")
    serve(app, host="0.0.0.0", port=port)
