from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import os, csv
from collections import defaultdict
import datetime
import time

app = Flask(__name__)
app.secret_key = "cambiar_esta_clave_por_una_segura"

# Configuración Azure Blob
connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = None
container_name = "pedidos"
blob_name = "pedidos.csv"

if connection_string:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)



# Productos disponibles (id, nombre, precio, imagen en static/img)
productos = [
    {"id": 1, "nombre": "Bolivia", "precio": 2.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 2, "nombre": "Portete", "precio": 3.00, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 3, "nombre": "Goyena", "precio": 3.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 4, "nombre": "Guayaka", "precio": 3.50, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 5, "nombre": "La 21", "precio": 4.00, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 43, "nombre": "Pollo", "precio": 4.00, "imagen": "hamburguesa.png", "tipo": "Hamburguesa"},
    {"id": 6, "nombre": "Margarita Guayaca", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    {"id": 7, "nombre": "Don Peperoni", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    {"id": 8, "nombre": "La Salamera", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    {"id": 9, "nombre": "La Vacona", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    {"id": 10, "nombre": "PolloChampi", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
    {"id": 11, "nombre": "Tocinetona", "precio": 1.50, "imagen": "pizza.png", "tipo": "Pizza Porción"},
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
    {"id": 40, "nombre": "Carne", "precio": 1.50, "imagen": "rapidito.png", "tipo": "Doriloco"},
    {"id": 41, "nombre": "Pollo", "precio": 1.75, "imagen": "rapidito.png", "tipo": "Doriloco"},
    {"id": 42, "nombre": "Mixto", "precio": 2.00, "imagen": "rapidito.png", "tipo": "Doriloco"},
    {"id": 19, "nombre": "Papipollo", "precio": 3.00, "imagen": "papipollo.png", "tipo": "Adicional"},
    {"id": 20, "nombre": "Salchipapa", "precio": 1.50, "imagen": "salchi.png", "tipo": "Adicional"},
    {"id": 21, "nombre": "Tocino", "precio": 0.75, "imagen": "tocino.png", "tipo": "Adicional"},
    {"id": 22, "nombre": "Salchicha", "precio": 0.75, "imagen": "salchicha.png", "tipo": "Adicional"},
    {"id": 23, "nombre": "Cheddar", "precio": 0.50, "imagen": "cheddar.png", "tipo": "Adicional"},
    {"id": 24, "nombre": "Piña", "precio": 0.50, "imagen": "piña.png", "tipo": "Adicional"},
    {"id": 25, "nombre": "Huevo", "precio": 0.50, "imagen": "huevo.png", "tipo": "Adicional"},
    {"id": 44, "nombre": "Papas", "precio": 1.00, "imagen": "papas.png", "tipo": "Adicional"},
    {"id": 45, "nombre": "Carne", "precio": 0.50, "imagen": "carne.png", "tipo": "Adicional"},
    {"id": 46, "nombre": "Pollo", "precio": 0.50, "imagen": "pollo.png", "tipo": "Adicional"},
    {"id": 47, "nombre": "Pulled Pork", "precio": 0.50, "imagen": "pork.png", "tipo": "Adicional"},
    {"id": 26, "nombre": "Agua", "precio": 0.50, "imagen": "agua.png", "tipo": "Bebida"},
    {"id": 27, "nombre": "Coca Cola Ori", "precio": 0.60, "imagen": "cola.png", "tipo": "Bebida"},
    {"id": 28, "nombre": "Fiora", "precio": 0.50, "imagen": "fiora.png", "tipo": "Bebida"},
    {"id": 29, "nombre": "Fanta", "precio": 0.75, "imagen": "fanta.png", "tipo": "Bebida"},
    {"id": 48, "nombre": "Sprite", "precio": 0.75, "imagen": "sprite.png", "tipo": "Bebida"},
    {"id": 30, "nombre": "Margarita Guayaca", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 31, "nombre": "Don Peperoni", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 32, "nombre": "La Salamera", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 33, "nombre": "La Vacona", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 34, "nombre": "PolloChampi", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 35, "nombre": "Tocinetona", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"},
    {"id": 36, "nombre": "Hawaiaca", "precio": 14.00, "imagen": "pizzaent.png", "tipo": "Pizza Entera"}
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


##@app.route("/cerrar_pedido/<pedido_id>")
##def cerrar_pedido(pedido_id):
##    """Eliminar por completo un pedido"""
##    if pedido_id in pedidos:
##        del pedidos[pedido_id]
##    return redirect(url_for("index"))


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
            precio_final = 7.00
        elif tamano == "Grande":
            precio_final = 14.00

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
        if tamano == "250ml":
            precio_final = 0.50
        elif tamano == "500ml":
            precio_final = 0.75
        
    #28Fiora,29fanta,48sprite

    global pedidos, pedido_counter


    # Si el pedido está cerrado, no permitir agregar
    if pedidos:
        ultimo_pedido = pedidos[max(pedidos.keys())]
        if ultimo_pedido and ultimo_pedido[-1].get("cerrado"):
            return jsonify({"error": "Este pedido está cerrado"}), 400



    # 📌 Usar el último pedido creado, o crear uno si no hay
    if not pedidos:
        pedidos[pedido_counter] = []
    pedido_id = max(pedidos.keys())

    nuevo_item = {
        "nombre": producto["nombre"] + (f" ({tamano})" if tamano else ""),
        "precio": precio_final,
        "imagen": producto["imagen"],
        "tipo": producto["tipo"]
    }

    pedidos[pedido_id].append(nuevo_item)

##   # 📌 Fecha y hora con time.strftime()
##    fecha = time.strftime("%d-%m-%Y")
##    hora = time.strftime("%H:%M:%S")
##
##    # Guardar en CSV
##    archivo = "pedidos.csv"
##    #archivo_nuevo = not os.path.exists(archivo_csv)
##
##    with open(archivo, mode="a", newline="") as f:
##        writer = csv.writer(f, delimiter=";")
##        writer.writerow([fecha, hora, producto["id"], producto["tipo"], producto["nombre"], producto["precio"], tamano if tamano else "N/A"])
##    


    guardar_pedido_en_blob(pedido_id, pedidos[pedido_id])
   
    return jsonify(generar_respuesta_carrito())


def guardar_pedido_en_blob(pedido_id, pedido_items):
    f#echa_hora = time.strftime("%d/%m/%Y %H:%M")
    # 📌 Fecha y hora con time.strftime()
    fecha = time.strftime("%d-%m-%Y")
    hora = time.strftime("%H:%M:%S")
    nombre_archivo = f"pedido_{pedido_id}.csv"

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    
    #writer.writerow(["Fecha", "Hora", "PedidoID", "Tipo", "Producto", "Precio", "Tamano"])

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
            if item.get("tamano"):
                nombre_final += f" ({item['tamano']})"
                writer.writerow([fecha, hora, producto["id"], producto["tipo"], producto["nombre"], producto["precio"], tamano if tamano else "N/A"])


    # Subir el CSV actualizado a Blob Storage
    if blob_service_client:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(output.getvalue(), overwrite=True)
        print(f"Pedido {pedido_id} guardado en Azure Blob Storage ({blob_name})")
    else:
        # Guardado local si no hay conexión a Azure
        archivo_csv = "pedidos.csv"
        with open(archivo_csv, mode="a", newline="", encoding="utf-8") as file:
            local_writer = csv.writer(file, delimiter=";")
            if os.stat(archivo_csv).st_size == 0:
                local_writer.writerow(["FechaHora", "PedidoID", "Producto", "Precio", "Total", "PagoCliente", "Vuelto"])
            file.write(output.getvalue())
        print(f"Pedido {pedido_id} guardado en local ({archivo_csv})")



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
        tipo = int(data.get("tipo"))
        pago_cliente = float(data.get("pago_cliente"))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if pedido_id not in pedidos:
        return jsonify({"error": "Pedido no encontrado"}), 404

    # Calcular total del pedido
    total_pedido = sum(item["precio"] for item in pedidos[pedido_id] if not item["eliminado"])
    vuelto = pago_cliente - total_pedido


    # Eliminar pedido de la memoria después de cobrar
    del pedidos[pedido_id]

    return jsonify({"success": True, "vuelto": vuelto, "carrito": generar_respuesta_carrito(contar_eliminados=True)})



# Modificar producto de un pedido
@app.route("/modificar_item", methods=["POST"])
def modificar_item():
    data = request.get_json()
    try:
        pedido_id = int(data.get("pedido_id"))
        indice = int(data.get("indice"))
        nuevo_producto_id = int(data.get("nuevo_producto_id"))
        tamano = data.get("tamano")
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if pedido_id not in pedidos or indice < 0 or indice >= len(pedidos[pedido_id]):
        return jsonify({"error": "Producto no encontrado en pedido"}), 404

    nuevo_producto = next((p for p in productos if p["id"] == nuevo_producto_id), None)
    if not nuevo_producto:
        return jsonify({"error": "Nuevo producto no encontrado"}), 404

    precio_final = nuevo_producto["precio"]
    if nuevo_producto["tipo"] == "Pizza Entera" and tamano:
        if tamano == "Pequeña":
            precio_final = 4.50
        elif tamano == "Mediana":
            precio_final = 7.00
        elif tamano == "Grande":
            precio_final = 14.00
    if nuevo_producto["tipo"] == "Adicional" and nuevo_producto["id"]==19 and tamano:
        if tamano == "Pechuga":
            precio_final = 3.00
        elif tamano == "Cadera":
            precio_final = 3.00
        elif tamano == "Ala":
            precio_final = 2.50
        elif tamano == "Pierna":
            precio_final = 2.50
    if nuevo_producto["tipo"] == "Bebida" and (nuevo_producto["id"]==28 or nuevo_producto["id"]==29 or nuevo_producto["id"]==48) and tamano:
        if tamano == "250ml":
            precio_final = 0.50
        elif tamano == "500ml":
            precio_final = 0.75
    

    pedidos[pedido_id][indice] = {
        "nombre": nuevo_producto["nombre"] + (f" ({tamano})" if tamano else ""),
        "precio": precio_final,
        "imagen": nuevo_producto["imagen"],
        "tipo": nuevo_producto["tipo"],
        "eliminado": False
    }

    return jsonify(generar_respuesta_carrito(contar_eliminados=True))






if __name__ == "__main__":
    from waitress import serve
    import os
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)
