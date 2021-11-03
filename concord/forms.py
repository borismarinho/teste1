from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from concord.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    user_name = StringField('Nome do Usuário', validators=[DataRequired(message='Campo necessário')])
    email = StringField('E-mail', validators=[DataRequired(message='Campo necessário'), Email(message='Email invalido')])
    senha = PasswordField('Senha', validators=[DataRequired(message='Campo necessário'), Length(6, 20)])
    confirmacao = PasswordField('Confirmação da Senha', validators=[DataRequired(message='Campo necessário'), EqualTo('senha', message='Campo deve ser igual a campo de Senha')])
    botao_submit_criar_conta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Email já cadastrado. Cadastre-se com outro e-mail ou faça login pra continuar')



class FormEditarPerfil(FlaskForm):
    user_name = StringField('Nome do Usuário', validators=[DataRequired(message='Campo necessário')])
    email = StringField('E-mail', validators=[DataRequired(message='Campo necessário'), Email(message='Digite email valido')])

    curso_excel = BooleanField('Excel Impressionador')
    curso_vba = BooleanField('VBA Impressionador')
    curso_powerbi = BooleanField('Power BI Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_ppt = BooleanField('Apresentações Impressionadoras')
    curso_sql = BooleanField('SQL Impressionador')

    foto_perfil = FileField('Atualizar foto de perfil', validators=[FileAllowed(['jpg', 'png'], message='Formato Não Permitido, Use um arquivo jpg ou png')])
    botao_submit_editar_perfil = SubmitField('Confirmar edição')

    def validate_email(self, email):
        # veficar se o cara mudou de email
        if current_user.email != email.data:

            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuario cadastrado nesse E-mail. Informe outro E-mail')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(message='Campo necessário'), Email(message='Digite email valido')])
    senha = PasswordField('Senha', validators=[DataRequired(message='Campo necessário'), Length(6, 20, message='Senha deve ter entre 6 e 20 algoritimos')])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(message='Campo necessário'), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post aqui', validators=[DataRequired(message='Campo necessário')])
    botao_submit_criar_post = SubmitField('Criar Post')

