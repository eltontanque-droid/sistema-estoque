from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# -------------------------
# BANCO DE DADOS
# -------------------------

def conectar():
    return sqlite3.connect("estoque.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            codigo TEXT,
            preco REAL,
            estoque INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            contato TEXT,
            documento TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            tipo TEXT,
            quantidade INTEGER,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()

# -------------------------
# ROTAS
# -------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/produtos")
def produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()
    conn.close()
    return render_template("produtos.html", produtos=dados)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nome = request.form["nome"]
        codigo = request.form["codigo"]
        preco = float(request.form["preco"])
        estoque = int(request.form["estoque"])

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, codigo, preco, estoque) VALUES (?, ?, ?, ?)",
            (nome, codigo, preco, estoque)
        )
        conn.commit()
        conn.close()

        return redirect("/produtos")

    return render_template("add_produto.html")

# -------------------------
# MOVIMENTAÇÃO
# -------------------------

@app.route("/entrada/<int:id>")
def entrada(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE produtos SET estoque = estoque + 1 WHERE id = ?",
        (id,)
    )

    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data) VALUES (?, ?, ?, ?)",
        (id, "entrada", 1, datetime.now().strftime("%d/%m/%Y %H:%M"))
    )

    conn.commit()
    conn.close()

    return redirect("/produtos")

@app.route("/saida/<int:id>")
def saida(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE produtos SET estoque = estoque - 1 WHERE id = ? AND estoque > 0",
        (id,)
    )

    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data) VALUES (?, ?, ?, ?)",
        (id, "saida", 1, datetime.now().strftime("%d/%m/%Y %H:%M"))
    )

    conn.commit()
    conn.close()

    return redirect("/produtos")

# -------------------------
# HISTÓRICO
# -------------------------

@app.route("/movimentacoes")
def movimentacoes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT movimentacoes.id, produtos.nome, tipo, quantidade, data
        FROM movimentacoes
        JOIN produtos ON produtos.id = movimentacoes.produto_id
        ORDER BY movimentacoes.id DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    return render_template("movimentacoes.html", movimentacoes=dados)

# -------------------------
# FORNECEDORES
# -------------------------

@app.route("/fornecedores")
def fornecedores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fornecedores")
    dados = cursor.fetchall()
    conn.close()
    return render_template("fornecedores.html", fornecedores=dados)

@app.route("/add_fornecedor", methods=["GET", "POST"])
def add_fornecedor():
    if request.method == "POST":
        nome = request.form["nome"]
        contato = request.form["contato"]
        documento = request.form["documento"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO fornecedores (nome, contato, documento) VALUES (?, ?, ?)",
            (nome, contato, documento)
        )
        conn.commit()
        conn.close()

        return redirect("/fornecedores")

    return render_template("add_fornecedor.html")

# -------------------------
# EXECUÇÃO
# -------------------------

if __name__ == "__main__":
    criar_banco()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
