import os
import psycopg

def get_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        return psycopg.connect(DATABASE_URL)

    return psycopg.connect(
        host="localhost",
        user="postgres",
        password="1234",
        dbname="catalogo_filmes"
    )