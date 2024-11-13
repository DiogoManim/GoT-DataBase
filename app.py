from flask import Flask, render_template
import sqlite3

conn = sqlite3.connect('game_of_thrones.db')
app = Flask(__name__)

cur = conn.cursor()
cur.row_factory = sqlite3.Row

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<name>')
def panel(name):
    try:
        return render_template(f'components/{name}/{name}.html')
    except Exception as e:
        print(f"Erro ao carregar o painel: {e}")
        return "Página não encontrada", 404


if __name__ == '__main__':
    app.run(debug=True)
