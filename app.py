from flask import Flask, render_template, request, redirect, session
import os
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "clave_super_secreta_123"

# Obtener la URL de la base de datos desde Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        port=url.port
    )
    return conn

# Ruta principal
@app.route("/")
def inicio():
    return "Capacitara conectada a PostgreSQL 🚀"

# Ruta para inicializar la base de datos
@app.route("/init-db")
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            rol VARCHAR(50)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cursos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150),
            descripcion TEXT,
            modalidad VARCHAR(50),
            duracion VARCHAR(50),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    return "Tablas creadas correctamente 🚀"


# Crear administrador
@app.route("/create-admin")
def create_admin():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO usuarios (nombre, email, password, rol)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING;
    """, ("Juan Carlos", "juanroque2203@gmail.com", "America14", "admin"))

    conn.commit()
    cur.close()
    conn.close()

    return "Administrador creado 🚀"


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM usuarios WHERE email = %s AND password = %s",
            (email, password)
        )

        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["usuario"] = user[1]
            return redirect("/admin")
        else:
            return "Credenciales incorrectas"

    return render_template("login.html")


# PANEL ADMIN
@app.route("/admin")
def admin():
    if "usuario" not in session:
        return redirect("/login")

    return f"Bienvenido {session['usuario']} al panel administrador 🚀"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)