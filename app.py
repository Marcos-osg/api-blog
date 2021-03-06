from flask import Flask, jsonify, request, make_response
from cria_banco import app, Autor, Postagem, db
import json
import jwt
from datetime import datetime, timedelta
from functools import wraps


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        # Se temos um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token é inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})


 # Rota padrao 
@app.route('/')
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_postagens.append(postagem)
    return jsonify({'postagens':lista_postagens})

# obter postagem por id
@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_indice(autor,id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    postagem_atual['id_autor'] = postagem.id_autor
    return jsonify({'postagens': postagem_atual})


# Fazer postagens
@app.route('/postagem',methods=['POST'])
@token_obrigatorio
def criar_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(titulo=nova_postagem['titulo'],id_autor=nova_postagem['id_autor'])
    db.session.add(postagem)
    db.session.commit()
    return jsonify({'mensagem':'Postagem criada com sucesso'})

# alterar uma postagem
@app.route('/postagem/<int:id_postagem>',methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor,id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterada com sucessso'})

# Deletar uma postagem
@app.route('/postagem/<int:id_postagem>',methods=['DELETE'])
@token_obrigatorio
def exclui_postagem(autor,id_postagem):
    postagem_a_ser_excluida = Postagem.query.filter_by(
        id_postagem=id_postagem).first()
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrado uma postagem com este id'})
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})

# obter autores
@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)
    return jsonify ({'autores': lista_de_autores})

#obter autor por id
@app.route('/autores/<int:id_autor>',methods=['GET'])
@token_obrigatorio
def obter_autor_id(autor,id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        jsonify('Autor não encontrado')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    return jsonify({'autor': autor_atual})

#novo autor
@app.route('/autores',methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(nome=novo_autor['nome'],email=novo_autor['email'],senha=novo_autor['senha'])
    db.session.add(autor)
    db.session.commit()
    return jsonify({'mensagem':'Usuario criado com sucesso'})


#alterar autor por id
@app.route('/autores/<int:id_autor>',methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor,id_autor):
    usuario_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'Mensagem':'Este usuario nao foi encontrado'})
    try:
        if usuario_alterar['nome']:
            autor.nome = usuario_alterar['nome']
    except:
        pass
    try:
        if usuario_alterar['email']:
            autor.email = usuario_alterar['email']
    except:
        pass
    try:
        if usuario_alterar['senha']:
            autor.senha = usuario_alterar['senha']
    except:
        pass
    db.session.commit()
    return jsonify({'Mensagem':'Usuario alterado com sucesso'})


#excluir autor por id
@app.route('/autores/<int:id_autor>',methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor,id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'Mensagem':'Autor nao foi encontrado'})
    db.session.delete(autor_existente)
    db.session.commit()
    return jsonify({'Mensagem':'Autor excluido com sucesso'})


app.run(port=5000, host='localhost', debug=True)
