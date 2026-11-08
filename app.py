
import os
import sqlite3
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import check_password_hash


app = Flask(__name__)

# Configuración de seguridad
app.secret_key = os.environ.get("SECRET_KEY")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

DATABASE = os.environ.get("DATABASE_PATH", "datos.db")


# Verificar que las credenciales estén configuradas
if not app.secret_key:
    raise RuntimeError("Falta configurar SECRET_KEY")

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise RuntimeError("Faltan las credenciales del administrador")


# Conexión con SQLite
def conectar_db():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


# Crear tabla de registros
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


# Protección de páginas privadas
def requiere_login(funcion):
    @wraps(funcion)
    def funcion_protegida(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return funcion_protegida


# Página de inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("admin_logged_in"):
        return redirect(url_for("inicio"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        usuario_correcto = username == ADMIN_USERNAME

        contraseña_correcta = check_password_hash(
            ADMIN_PASSWORD_HASH,
            password
        )

        if usuario_correcto and contraseña_correcta:

            session.clear()
            session["admin_logged_in"] = True

            return redirect(url_for("inicio"))

        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos"
        )

    return render_template("login.html")


# Página principal protegida
@app.route("/")
@requiere_login
def inicio():

    conexion = conectar_db()

    registros = conexion.execute(
        "SELECT * FROM registros ORDER BY id DESC"
    ).fetchall()

    conexion.close()

    return render_template("index.html", registros=registros)


# Guardar registros: solamente el administrador
@app.route("/guardar", methods=["POST"])
@requiere_login
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


# Cerrar sesión
@app.route("/logout", methods=["POST"])
@requiere_login
def logout():

    session.clear()

    return redirect(url_for("login"))


# Inicializar la base de datos
crear_tabla()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
