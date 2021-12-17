from leposticheBI import database, login_menager
from datetime import datetime
from flask_login import UserMixin

@login_menager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)


class Empresa(database.Model):
    id = database.Column(database.Integer ,primary_key=True, nullable=False)
    nome = database.Column(database.String, nullable=False)
    resultado = database.relationship('EmpresaResultado', backref='resultado', lazy=True)

class EmpresaResultado(database.Model):
    id = database.Column(database.Integer,primary_key=True)
    id_empresa = database.Column(database.Integer, database.ForeignKey('empresa.id'), nullable=False)
    ano = database.Column(database.Integer, nullable=False)
    mes = database.Column(database.Integer, nullable=False)
    receita_bruta = database.Column(database.Float)
    rep_bruta = database.Column(database.Float)
    devolucao = database.Column(database.Float)
    ipi = database.Column(database.Float)
    cmv = database.Column(database.Float)
    icms_substituto = database.Column(database.Float)
    despesas_ven = database.Column(database.Float ,default=0)
    despesas_ocu = database.Column(database.Float , default=0)
    despesas_adm = database.Column(database.Float ,default=0)
    despesas_ger = database.Column(database.Float ,default=0)
    break_even = database.Column(database.Float ,default=0)
    sup_caixa = database.Column(database.Float ,default=0)
    val_sup_caixa = database.Column(database.Float ,default=0)
    per_imposto = database.Column(database.Float ,default=0)
    val_imposto = database.Column(database.Float ,default=0)
    despesas_rateadas = database.Column(database.Float ,default=0)
    tot_rec_liq = database.Column(database.Float ,default=0)
    tot_cmv = database.Column(database.Float ,default=0)
    lucro_bruto = database.Column(database.Float ,default=0)
    rep_bruto = database.Column(database.Float ,default=0)
    tot_adm = database.Column(database.Float ,default=0)
    rep_adm = database.Column(database.Float ,default=0)
    rep_ven = database.Column(database.Float ,default=0)
    tot_des = database.Column(database.Float ,default=0)
    rep_des = database.Column(database.Float ,default=0)
    ebit = database.Column(database.Float ,default=0)
    rep_ebit = database.Column(database.Float ,default=0)

class DespesasRateadas(database.Model):
    id = database.Column(database.Integer,primary_key=True)
    ano = database.Column(database.Integer, nullable=False)
    mes = database.Column(database.Integer, nullable=False)
    despesas_ger = database.Column(database.Float)
    despesas_adm = database.Column(database.Float)
    despesas_ocu = database.Column(database.Float)
    despesas_pro = database.Column(database.Float)

class Plano(database.Model):
    id = database.Column(database.Integer ,primary_key=True, nullable=False)
    descricao = database.Column(database.String, nullable=False)
    tipo = database.Column(database.String, nullable=False)
