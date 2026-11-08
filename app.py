
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Nombre de nuestra base de datos
DATABASE = "datos.db"


# Conectar con SQLite
def conectar_db():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


# Crear tabla si todavía no existe
def crear_tabla():
    conexion = conectar_db()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


# Página principal
@app.route("/")
def inicio():
    conexion = conectar_db()

    registros = conexion.execute(
        "SELECT * FROM registros ORDER BY id DESC"
    ).fetchall()

    conexion.close()

    return render_template("index.html", registros=registros)


# Recibir información del formulario
@app.route("/guardar", methods=["POST"])
def guardar():

    nombre = request.form.get("nombre", "").strip()
    mensaje = request.form.get("mensaje", "").strip()

    if nombre and mensaje:

        conexion = conectar_db()

        conexion.execute(
            "INSERT INTO registros (nombre, mensaje) VALUES (?, ?)",
            (nombre, mensaje)
        )

        conexion.commit()
        conexion.close()

    return redirect(url_for("inicio"))


# Iniciar aplicación
if __name__ == "__main__":

    crear_tabla()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
