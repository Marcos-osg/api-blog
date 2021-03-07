from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#cria um api flask
app = Flask(__name__)
#criar uma instancia sqlalchemy
app.config['SECRET_KEY'] = 'Teste123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' #nao esquecer de sempre ter 3 /

db = SQLAlchemy(app)
db: SQLAlchemy

#definir a estrutura da tabela postagem
class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))

#definir a estrutura da tabela autor
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    Postagens = db.relationship('Postagem')

def inicializar_banco():
    db.drop_all()
    db.create_all()
    #administradores
    autor = Autor(nome='Marcos',email='devmarcos.py@gmail.com',senha='Marcos123',admin=True)
    db.session.add(autor)
    db.session.commit()

if __name__ == "__main__":
    inicializar_banco()