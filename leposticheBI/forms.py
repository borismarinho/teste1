from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from leposticheBI.models import Usuario, Plano
from flask_login import current_user
from pathlib import Path

class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(message='Campo Obrigadorio')])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()

        if usuario:
            raise ValidationError('E-mail Já Cadastrado')

class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormDespesasGerais(FlaskForm):
    ano = IntegerField('Ano', validators=[DataRequired(message='Campo Obrigadorio')])
    mes = SelectField('Mês', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    des_adm = FloatField('Despesas administrativas')
    des_ger = FloatField('Despesas Gerais')
    des_pro = FloatField('Despesas de prolabore')
    des_ocu = FloatField('Despesas com Ocupação')
    opcao = StringField('')
    botao_submit_despesa = SubmitField('Salvar')

    @staticmethod
    def validate_mes(self, mes):
        if mes.data < 1 or mes.data > 12:
           raise ValidationError('Mes Invalido')

    @staticmethod
    def validate_ano(self, ano):
        if len(str(ano.data)) != 4:
           raise ValidationError('Ano Invalido')

class FormEmpresas(FlaskForm):
    id = IntegerField('Código da Empresa', validators=[DataRequired()])
    nome = StringField('Nome da Empresa', validators=[DataRequired(), Length(2, 40)])
    botao_submit = SubmitField('Incluir')

class FormDespesasEmpresa(FlaskForm):
    nome = StringField('Empresa')
    ano = IntegerField('Ano')
    mes = SelectField('Mês', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    des_adm = FloatField('Despesas administrativas')
    des_ocu = FloatField('Despesas de ocupação')
    des_ven = FloatField('Despesas com Vendas')
    des_ger = FloatField('Despesas Gerais')
    break_even = FloatField('Break Even')
    sup_caixa = FloatField('Suprimento de Caixa %')
    per_imposto = FloatField('Imposto sobre Venda %')
    botao_submit = SubmitField('Salvar')

    @staticmethod
    def validate_sup_caixa(self, sup_caixa):
        if sup_caixa.data > 100:
           raise ValidationError('Suprimento não pode ser maior que 100%')

    @staticmethod
    def validate_imposto(self, imposto):
        if imposto.data > 100:
           raise ValidationError('Imposto não pode ser maior que 100%')


class FormImportar(FlaskForm):
    produtos = FileField('Arquivo de Produtos', validators=[DataRequired(), FileAllowed(['csv' ])])
    vendas = FileField('Arquivo de Vendas  ', validators=[DataRequired() , FileAllowed(['csv' ])])
    botao_submit = SubmitField('Importar')

class FormFechaPeriodo(FlaskForm):
    ano = IntegerField('Ano', validators=[DataRequired(message='Campo Obrigadorio')])
    mes = SelectField('Mês', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    botao_submit = SubmitField('Processar')

    @staticmethod
    def validate_mes(self, mes):
        if mes.data < 1 or mes.data > 12:
           raise ValidationError('Mes Invalido')

    @staticmethod
    def validate_ano(self, ano):
        if len(str(ano.data)) != 4:
           raise ValidationError('Ano Invalido')

class FormComparaPeriodo(FlaskForm):
    int1_ano_ini = IntegerField('Ano Inicial', validators=[DataRequired()])
    int1_mes_ini = SelectField('Mês Inicial', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    int1_ano_fin = IntegerField('Ano Final', validators=[DataRequired()])
    int1_mes_fin = SelectField('Mês Final', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    int2_ano_ini = IntegerField('Ano Inicial', validators=[DataRequired()])
    int2_mes_ini = SelectField('Mês Inicial', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    int2_ano_fin = IntegerField('Ano Final', validators=[DataRequired()])
    int2_mes_fin = SelectField('Mês Final', coerce=int, choices=[('01', 'JAN'),('02', 'FEV'),('03', 'MAR'),('04', 'ABR'),('05', 'MAI'),('06', 'JUN'),('07', 'JUL'),('08', 'AGO'),('09', 'SET'),('10', 'OUT'),('11', 'NOV'),('12', 'DEZ') ])
    empresa = SelectField(u'Empresa', coerce=int)
    todas_empresas = BooleanField('Todos as empresas')
    botao_submit = SubmitField('Processar')

class FormPlano(FlaskForm):
    id = IntegerField('Código', validators=[DataRequired(message='Campo Obrigadorio')])
    descricao = StringField('Descricao', validators=[DataRequired(message='Campo Obrigadorio'),Length(min=10, message='Descrição deve ser maior 9 caracteres')])
    tipo = SelectField('Tipo', coerce=str, choices=[('ADM', 'ADMINSTRATIVA'),('OCU', 'OCUPAÇÃO'), ('VEN', 'VENDAS'),('GER', 'GASTAS GERAIS'),('PRO', 'PROLABORE'),('IMP', 'IMPOSTO S/VENDA'),('EXC', 'NÃO CONSIDERAR')])
    opcao = StringField('')
    botao_submit = SubmitField('Salvar')

    @staticmethod
    def validate_tipo(self, tipo):
        lista_tipo = ['ADM','OCU','EXC','VEN','GER','PRO']
        if tipo.data.upper() in lista_tipo:
            pass
        else:
           raise ValidationError('Opção invalida some ADM OCU EXC VEN GER PRO')

    @staticmethod
    def validate_codigo(self, codigo):
        plano = Plano.query.get(codigo.data)

        if plano:
            raise ValidationError('Código Já Cadastrado')

class FormImportarDespesas(FlaskForm):
    despesas = FileField('Arquivo de Produtos', validators=[DataRequired(), FileAllowed(['csv','xlsx' ])])
    botao_submit = SubmitField('Importar')
