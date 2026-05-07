import os
from functools import wraps
import uuid

from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session,
    flash
)
from psycopg2.extras import RealDictCursor

from database import (
    get_connection,
    buscar_usuario_por_email,
    cadastrar_usuario
)

import re

from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


user = {
    "dywxty@gmail.com": "1234"}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api')
@login_required

def home():
    return redirect(url_for("listar_filmes"))


@app.route('/filmes')
@login_required

def listar_filmes():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM filmes")
        filmes = cursor.fetchall()
        conn.close()
        return render_template("index.html", filmes=filmes)
    except Exception as ex:
        print("ERRO LISTAR:", ex)
        return str(ex)


@app.route("/novo", methods=["GET", "POST"])
@login_required

def novo_filme():
    if request.method == "POST":
        try:
            titulo = request.form.get("titulo")
            genero = request.form.get("genero")
            ano = request.form.get("ano")

            imagem = request.files.get("imagem")

            if not imagem or imagem.filename == "":
                return "nenhuma imagem foi enviada"

            extensao = imagem.filename.rsplit('.', 1)[-1].lower()
            if extensao not in ["jpg", "jpeg", "png"]:
                return "formato inválido"

            nome_arquivo = f"{uuid.uuid4()}.{extensao}"
            caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)

            imagem.save(caminho_arquivo)

            caminho_db = f"uploads/{nome_arquivo}"

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO filmes (titulo, genero, ano, url_capa) VALUES (%s, %s, %s, %s)",
                (titulo, genero, ano, caminho_db)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("listar_filmes"))

        except Exception as ex:
            print("ERRO SALVAR:", ex)
            return "erro ao salvar filme"

    return render_template("novo_filme.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required

def editar_filme(id):

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":

        titulo = request.form.get("titulo")
        genero = request.form.get("genero")
        ano = request.form.get("ano")

        cursor.execute(
            """
            UPDATE filmes
            SET titulo = %s,
                genero = %s,
                ano = %s
            WHERE id = %s
            """,
            (titulo, genero, ano, id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("listar_filmes"))

    cursor.execute(
        "SELECT * FROM filmes WHERE id = %s",
        (id,)
    )

    filme = cursor.fetchone()

    conn.close()

    return render_template(
        "editar_filme.html",
        filme=filme
    )

@app.route("/deletar/<int:id>", methods=["POST"])
@login_required

def deletar_filme(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filmes WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for("listar_filmes"))
    except Exception as ex:
        print("ERRO DELETAR:", ex)
        return "erro ao deletar"


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("password")

        usuario = buscar_usuario_por_email(email)

        if not usuario:

            return render_template(
                "login.html",
                erro="Usuário não encontrado"
            )

        if not check_password_hash(usuario["senha"], senha):

            return render_template(
                "login.html",
                erro="Senha incorreta"
            )

        session["user"] = usuario["email"]

        return redirect(url_for("listar_filmes"))

    return render_template(
        "login.html",
        erro=None
    )
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("password")

        # mínimo 8 caracteres
        if len(senha) < 8:

            return render_template(
                "cadastro.html",
                erro="A senha deve possuir no mínimo 8 caracteres"
            )

        # caractere especial
        if not re.search(r'[@$!%*?&]', senha):

            return render_template(
                "cadastro.html",
                erro="A senha deve possuir caractere especial"
            )

        usuario = buscar_usuario_por_email(email)

        if usuario:

            return render_template(
                "cadastro.html",
                erro="E-mail já cadastrado"
            )

        cadastrar_usuario(nome, email, senha)

        return redirect(url_for("login"))

    return render_template(
        "cadastro.html",
        erro=None
    )


@app.route("/logout")

def logout():

    session.pop("user", None)

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)