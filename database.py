import os
import psycopg

def get_connection():
    DATABASE_URL = os.environ.get("postgresql://neondb_owner:npg_Qnv4i7XHwbUd@ep-rapid-truth-amjduagq-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

    if DATABASE_URL:
        return psycopg.connect(DATABASE_URL)

    return psycopg.connect(
        host="localhost",
        user="postgres",
        password="1234",
        dbname="catalogo_filmes"
    )