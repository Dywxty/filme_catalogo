import os
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import get_connection

app = Flask(__name__)

# garante que a pasta uploads existe
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return redirect(url_for("listar_filmes"))


@app.route('/filmes', methods=['GET'])
def listar_filmes():
    sql = "SELECT * FROM filmes"
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        filmes = cursor.fetchall()
        conn.close()
        return render_template("index.html", filmes=filmes)
    except Exception as ex:
        print("ERRO LISTAR FILMES:", str(ex))
        return "erro ao listar filmes"


@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    sql = "INSERT INTO filmes (titulo, genero, ano, url_capa) VALUES (%s, %s, %s, %s)"

    if request.method == "POST":
        titulo = request.form["titulo"]
        genero = request.form["genero"]
        ano = request.form["ano"]

        imagem = request.files.get("imagem")

        if not imagem or imagem.filename == "":
            return "nenhuma imagem foi enviada"

        extensoes_permitidas = ["jpg", "jpeg", "png"]
        extensao = imagem.filename.split(".")[-1].lower()

        if extensao not in extensoes_permitidas:
            return "arquivo inválido (use jpg, jpeg ou png)"

        # gera nome único (hash)
        nome_unico = f"{uuid.uuid4()}.{extensao}"

        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_unico)
        imagem.save(caminho_arquivo)

        caminho_db = f"/static/uploads/{nome_unico}"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, [titulo, genero, ano, caminho_db])
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))
        except Exception as ex:
            print("ERRO SALVAR FILME:", str(ex))
            return "erro ao salvar filme"

    return render_template("novo_filme.html")


@app.route("/deletar/<int:id>", methods=["POST"])
def deletar_filme(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filmes WHERE id = %s", [id])
        conn.commit()
        conn.close()
        return redirect(url_for("listar_filmes"))
    except Exception as ex:
        print("ERRO DELETAR:", str(ex))
        return "erro ao deletar"


if __name__ == '__main__':
    app.run(debug=True)