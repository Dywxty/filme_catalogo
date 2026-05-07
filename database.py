import psycopg2
import os

from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash


def get_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1234",
        database="catalogo_filmes"
    )


# =========================================
# BUSCAR USUÁRIO PELO EMAIL
# =========================================

def buscar_usuario_por_email(email):

    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM usuario WHERE email = %s",
        (email,)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return usuario


# =========================================
# CADASTRAR USUÁRIO
# =========================================

def cadastrar_usuario(nome, email, senha):

    conn = get_connection()

    cursor = conn.cursor()

    senha_criptografada = generate_password_hash(senha)

    cursor.execute("""
        INSERT INTO usuario (nome, email, senha)
        VALUES (%s, %s, %s)
    """, (nome, email, senha_criptografada))

    conn.commit()

    cursor.close()
    conn.close()