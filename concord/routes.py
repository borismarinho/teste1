from flask import render_template, redirect, url_for, flash, request, abort
from concord import app, database, bcrypt
from concord.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from concord.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image



@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('Homepage.html', posts=posts)


@app.route("/contatos")
def contatos():
    return render_template('contato.html')


@app.route("/lista_usuarios")
@login_required
def usuarios():
    lista_usarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usarios=lista_usarios)


@app.route("/teste")
def teste():
    return render_template('teste.html')


@app.route("/Login_Criar_Conta", methods=['GET', 'POST'])
def criar_conta():
    form_login = FormLogin()
    form_conta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            # fez login com sucesso
            # exibir mensagem de login bem sucedido
            flash(f'Login feito com sucesso no email: {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                # voltar para homepage
                return redirect(url_for('home'))
        else:
            flash(f'Falha no Login, Email ou Senha incorretos', 'alert-danger')
    if form_conta.validate_on_submit() and 'botao_submit_criar_conta' in request.form:
        #criar usuario
        senha_crypt = bcrypt.generate_password_hash(form_conta.senha.data)
        usuario = Usuario(username=form_conta.user_name.data, email=form_conta.email.data, senha=senha_crypt)
        #adicionar a sessão no banco de dados
        database.session.add(usuario)
        #commit na sessão
        database.session.commit()
        #criou conta com sucesso
        flash(f'Conta criada para o E-mail: {form_conta.email.data}', 'alert-success')
        #voltar para homepage
        return redirect(url_for('home'))
    return render_template('Login.html', form_login=form_login, form_conta=form_conta)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route("/post/criar", methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criar_post.html', form=form)


def salva_imagem(imagem):
    # adicionar um código aleatório no nome da imagem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    # reduzir o tamanho da imagem
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    # salvar foto na pasta foto_perfil
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)



@app.route("/perfil/editar", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.user_name.data
        if form.foto_perfil.data:
            # mudar o campo foto perfil do usuario para o novo nome da foto
            nome_imagem = salva_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash('Perfil Atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.user_name.data = current_user.username
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form)


#<post_id> representa uma variavel
@app.route("/post/<post_id>", methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
        #logica de editar post
    else:
        form = None
    return render_template("post.html", post=post, form=form)


@app.route("/post/<post_id>/excluir", methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluido com Sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)
        return redirect(url_for('home'))