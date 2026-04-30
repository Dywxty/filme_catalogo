import psycopg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    if DATABASE_URL:
        return psycopg.connect(DATABASE_URL)

    return psycopg.connect(
        host="localhost",
        user="postgres",
        password="1234",
        dbname="catalogo_filmes"
    )


def init_table():
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            genero VARCHAR(100),
            ano VARCHAR(10),
            url_capa TEXT
        );
        """)

        conn.commit()
        conn.close()
        print("Tabela pronta!")

    except Exception as e:
        print("Erro:", e)


if __name__ == "__main__":
    init_table()