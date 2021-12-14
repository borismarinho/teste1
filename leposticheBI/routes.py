from flask import render_template, redirect, url_for, flash, request, abort
from leposticheBI import app, database, bcrypt
from leposticheBI.forms import FormLogin, FormCriarConta, FormDespesasGerais, FormEmpresas, FormDespesasEmpresa, FormImportar, FormFechaPeriodo, FormComparaPeriodo, FormPlano, FormImportarDespesas
from leposticheBI.models import Usuario, Empresa , EmpresaResultado, DespesasRateadas, Plano , EmpresaResultado
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from pathlib import Path
from datetime import datetime
import pyodbc as bd
import pandas as pd
from sqlalchemy import func

@app.route('/')
def home():
    usuario = Usuario.query.all()

    if usuario:
        if current_user.is_authenticated:
            return redirect(url_for('tela_principal'))
        else:
            return redirect(url_for('login'))
    else:
       return redirect(url_for('cria_conta'))


@app.route('/tela_principal')
@login_required
def tela_principal():
    empresas = Empresa.query.all()
    resultados = EmpresaResultado.query.all()

    ano = []
    lista_ano = []
    dicio_ano = {}
    ano_mes = []
    lista_ano_mes = []
    dicio_ano_mes = {}
    dicio_emp = {}
    
    for resultado in resultados:

        # converte em formato brasileiro
        resultado.c_receita_bruta = formatacao(resultado.receita_bruta)
        resultado.c_rep_bruta = formatacao(resultado.rep_bruta * 100)
        resultado.c_devolucao = formatacao(resultado.devolucao)
        resultado.c_val_imposto = formatacao(resultado.val_imposto)
        resultado.c_tot_rec_liq = formatacao(resultado.tot_rec_liq)
        resultado.c_tot_cmv = formatacao(resultado.tot_cmv)
        resultado.c_lucro_bruto = formatacao(resultado.lucro_bruto)
        resultado.c_rep_bruto = formatacao(resultado.rep_bruto)
        resultado.c_tot_adm = formatacao(resultado.tot_adm)
        resultado.c_rep_adm = formatacao(resultado.rep_adm)
        resultado.c_despesas_ven = formatacao(resultado.despesas_ven + resultado.despesas_ocu)
        resultado.c_rep_ven = formatacao(resultado.rep_ven)
        resultado.c_tot_des = formatacao(resultado.tot_des)
        resultado.c_rep_des = formatacao(resultado.rep_des)
        resultado.c_ebit = formatacao(resultado.ebit)
        resultado.c_rep_ebit = formatacao(resultado.rep_ebit)

        # acumula ano
        if not resultado.ano in ano:
            ano.append(resultado.ano)
            dicio_ano[resultado.ano]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        dicio_ano[resultado.ano][0] += resultado.receita_bruta
        dicio_ano[resultado.ano][1] += resultado.devolucao
        dicio_ano[resultado.ano][2] += resultado.val_imposto
        dicio_ano[resultado.ano][3] += resultado.tot_rec_liq
        dicio_ano[resultado.ano][4] += resultado.tot_cmv
        dicio_ano[resultado.ano][5] += resultado.lucro_bruto

        if resultado.tot_rec_liq > 0:
           dicio_ano[resultado.ano][6] = resultado.lucro_bruto / resultado.tot_rec_liq * 100
           dicio_ano[resultado.ano][7] += resultado.tot_adm
           dicio_ano[resultado.ano][8] = resultado.tot_adm / resultado.tot_rec_liq * 100
           dicio_ano[resultado.ano][9] += resultado.despesas_ven + resultado.despesas_ocu
           dicio_ano[resultado.ano][10] = (resultado.despesas_ven + resultado.despesas_ocu)  / resultado.tot_rec_liq * 100
           dicio_ano[resultado.ano][11] += resultado.tot_des
           dicio_ano[resultado.ano][12] = resultado.tot_des / resultado.tot_rec_liq * 100
           dicio_ano[resultado.ano][13] += resultado.ebit
           dicio_ano[resultado.ano][14] = resultado.ebit / resultado.tot_rec_liq * 100

        # acumula mês

        tem = str(resultado.ano) + '_' + str(resultado.mes)

        if not tem in ano_mes:
            ano_mes.append(tem)
            dicio_ano_mes[tem] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        dicio_ano_mes[tem][0] += resultado.receita_bruta
        dicio_ano_mes[tem][1] += resultado.devolucao
        dicio_ano_mes[tem][2] += resultado.val_imposto
        dicio_ano_mes[tem][3] += resultado.tot_rec_liq
        dicio_ano_mes[tem][4] += resultado.tot_cmv
        dicio_ano_mes[tem][5] += resultado.lucro_bruto

        if resultado.tot_rec_liq > 0:
           dicio_ano_mes[tem][6] = resultado.lucro_bruto / resultado.tot_rec_liq * 100
           dicio_ano_mes[tem][7] += resultado.tot_adm
           dicio_ano_mes[tem][8] = resultado.tot_adm / resultado.tot_rec_liq * 100
           dicio_ano_mes[tem][9] += resultado.despesas_ven + resultado.despesas_ocu
           dicio_ano_mes[tem][10] = (resultado.despesas_ven + resultado.despesas_ocu) / resultado.tot_rec_liq * 100
           dicio_ano_mes[tem][11] += resultado.tot_des
           dicio_ano_mes[tem][12] = resultado.tot_des / resultado.tot_rec_liq * 100
           dicio_ano_mes[tem][13] += resultado.ebit
           dicio_ano_mes[tem][14] = resultado.ebit / resultado.tot_rec_liq * 100


    for a in dicio_ano_mes:
        for i in range(15):
            dicio_ano_mes[a][i] = formatacao(dicio_ano_mes[a][i])

    for a in dicio_ano:
        for i in range(15):
            dicio_ano[a][i] = formatacao(dicio_ano[a][i])

    return render_template('tela_principal.html',empresas=empresas, resultados=resultados, dicio_ano=dicio_ano, dicio_ano_mes=dicio_ano_mes)

def formatacao(valor):
    if valor != None:
       converter = f'{valor:_.2f}'
       return converter.replace('.', ',').replace('_', '.')
    else:
        return '0,0'

@app.route('/fecha_periodo', methods=['GET', 'POST'])
@login_required
def fecha_periodo():
    form = FormFechaPeriodo()

    if form.validate_on_submit():
        resultados = EmpresaResultado.query.filter_by(ano=form.ano.data, mes=form.mes.data)
        despesa = DespesasRateadas.query.filter_by(ano=form.ano.data, mes=form.mes.data).first()
        despesa_rateada = 0

        if despesa:
            despesa_rateada = despesa.despesas_adm + despesa.despesas_ocu + despesa.despesas_pro + despesa.despesas_ger

        for resultado in resultados:
            resultado.despesas_rateadas = despesa_rateada * resultado.rep_bruta

            resultado.val_sup_caixa = resultado.cmv * resultado.sup_caixa / 100
            resultado.tot_rec_liq = resultado.receita_bruta - resultado.val_imposto - resultado.devolucao
            # total do CMV
            resultado.tot_cmv = resultado.cmv + resultado.ipi + resultado.val_sup_caixa + resultado.icms_substituto
            # lucro Bruto
            resultado.lucro_bruto = resultado.tot_rec_liq - resultado.tot_cmv
            resultado.rep_bruto = resultado.lucro_bruto / resultado.tot_rec_liq * 100
            # total da despesas administrativas sem vendas
            resultado.tot_adm = resultado.despesas_adm  + resultado.despesas_rateadas
            resultado.rep_adm = resultado.tot_adm / resultado.tot_rec_liq * 100
            # rep vendas sobre receita liquida
            resultado.rep_ven = (resultado.despesas_ven + resultado.despesas_ocu) / resultado.tot_rec_liq * 100
            # total da despesas administrativas com vendas
            resultado.tot_des = resultado.despesas_ven + resultado.despesas_ocu + resultado.tot_adm
            resultado.rep_des = resultado.tot_des / resultado.tot_rec_liq * 100
            # calculo EBIT
            resultado.ebit = resultado.lucro_bruto - resultado.tot_des
            resultado.rep_ebit = resultado.ebit / resultado.tot_rec_liq * 100
            database.session.commit()
        return redirect(url_for('tela_principal'))

    return render_template('fecha_periodo.html', form=form)

@app.route('/mostra_despesas')
@login_required
def mostra_despesas():
    despesas = DespesasRateadas.query.all()

    for despesa in despesas:
        despesa.despesas_ger = formatacao(despesa.despesas_ger)
        despesa.despesas_ocu = formatacao(despesa.despesas_ocu)
        despesa.despesas_adm = formatacao(despesa.despesas_adm)
        despesa.despesas_pro = formatacao(despesa.despesas_pro)
    return render_template('mostra_despesas.html', despesas=despesas)

@app.route('/edita_despesas/<despesa_id>' , methods=['GET', 'POST'])
@login_required
def edita_despesas(despesa_id):
    form = FormDespesasGerais()
    despesa = DespesasRateadas.query.get(despesa_id)


    if 'botao_submit_despesa' in request.form:
        despesa.despesas_adm = form.des_adm.data
        despesa.despesas_ocu = form.des_ocu.data
        despesa.despesas_pro = form.des_pro.data
        despesa.despesas_ger = form.des_ger.data
        database.session.commit()
        return redirect(url_for('mostra_despesas'))

    form.ano.data = despesa.ano
    form.mes.data = despesa.mes
    form.des_adm.data = despesa.despesas_adm
    form.des_ocu.data = despesa.despesas_ocu
    form.des_pro.data = despesa.despesas_pro
    form.des_ger.data = despesa.despesas_ger
    form.opcao.data = 'A'
    return render_template('edita_despesas.html', form=form)

@app.route('/incluir_despesas', methods=['GET', 'POST'])
@login_required
def incluir_despesas():
    form = FormDespesasGerais()

    if form.validate_on_submit():
        despesa = DespesasRateadas(ano=form.ano.data, mes=form.mes.data, despesas_pro=form.des_pro.data,despesas_adm=form.des_adm.data,despesas_ocu=form.des_ocu.data,despesas_ger=form.des_ocu.data)
        database.session.add(despesa)
        database.session.commit()
        return redirect(url_for('mostra_despesas'))
    return render_template('edita_despesas.html', form=form )

@app.route('/excluir_despesa/<despesa_id>', methods=['GET', 'POST'])
@login_required
def excluir_despesa(despesa_id):
    despesa = DespesasRateadas.query.get(despesa_id)

    if despesa:
        database.session.delete(despesa)
        database.session.commit()
        return redirect(url_for('mostra_despesas'))
    else:
        abort(403)

@app.route('/empresa')
@login_required
def empresas():
    lista_empresas = Empresa.query.all()
    return render_template('empresas.html', lista_empresas=lista_empresas)

@app.route('/mostra_despesas_empresa')
@login_required
def mostra_despesas_empresa():
    despesas = EmpresaResultado.query.all()

    for despesa in despesas:
        despesa.con_despesas_ven = formatacao(despesa.despesas_ven + despesa.despesas_ocu)
        despesa.con_despesas_ocu = formatacao(despesa.val_imposto)
        despesa.con_despesas_adm = formatacao(despesa.despesas_adm)
        despesa.con_despesas_ger = formatacao(despesa.despesas_ger)
        despesa.con_break_even = formatacao(despesa.break_even)
        despesa.con_sup_caixa = formatacao(despesa.sup_caixa)
        despesa.con_per_imposto = formatacao(despesa.per_imposto)

    return render_template('mostra_despesas_empresa.html', despesas=despesas)

@app.route('/edita_despesas_empresa/<despesa_id>' , methods=['GET', 'POST'])
@login_required
def edita_despesas_empresa(despesa_id):
    form = FormDespesasEmpresa()
    despesa = EmpresaResultado.query.get(despesa_id)

    if 'botao_submit' in request.form and despesa:
        despesa.break_even = form.break_even.data
        despesa.sup_caixa = form.sup_caixa.data

        database.session.commit()
        return redirect(url_for('mostra_despesas_empresa'))

    form.ano.data = despesa.ano
    form.mes.data = despesa.mes
    form.nome.data = despesa.resultado.nome
    form.break_even.data = despesa.break_even
    form.sup_caixa.data = despesa.sup_caixa
    return render_template('edita_despesas_empresa.html', form=form)

def salvar_arquivo(arquivo):
    caminho_completo = os.path.join(app.root_path, 'static/planilhas', arquivo.filename)
    arquivo.save(caminho_completo)
    return caminho_completo

@app.route('/importar' , methods=['GET', 'POST'])
@login_required
def importar():
    form = FormImportar()

    if form.validate_on_submit():
        caminho_produto = salvar_arquivo(form.produtos.data)
        caminho_vendas = salvar_arquivo(form.vendas.data)
        produtos_df = pd.read_csv(caminho_produto, sep=';', encoding='latin1')
        vendas_df = pd.read_csv(caminho_vendas, sep=';', encoding='latin1')
        coluna_produto = ['Código Produto', 'Setor', 'Linha', 'Marca', 'Fornecedor', 'Custo ICMS', 'IPI',
                          'Valor Substituição', 'Configuração Tributária']
        produtos_df = produtos_df[coluna_produto]
        vendas_df = vendas_df.merge(produtos_df, on='Código Produto')
        # transforma data no formato objeto em date
        vendas_df['Data Documento'] = pd.to_datetime(vendas_df['Data Documento'], format='%d/%m/%Y')
        # cria compos ano e mes
        vendas_df['Ano da Venda'] = vendas_df['Data Documento'].dt.year
        vendas_df['Mes da Venda'] = vendas_df['Data Documento'].dt.month
        # converte valores em numerico
        vendas_df['Preço Líquido'] = vendas_df['Preço Líquido'].apply(lambda x: str(x).replace(',', '.'))
        vendas_df['Preço Líquido'] = vendas_df['Preço Líquido'].astype(float)
        vendas_df['IPI'] = vendas_df['IPI'].apply(lambda x: str(x).replace(',', '.'))
        vendas_df['IPI'] = vendas_df['IPI'].astype(float)
        vendas_df['Custo ICMS'] = vendas_df['Custo ICMS'].apply(lambda x: str(x).replace(',', '.'))
        vendas_df['Custo ICMS'] = vendas_df['Custo ICMS'].astype(float)
        vendas_df['Total'] = vendas_df['Total'].apply(lambda x: str(x).replace(',', '.'))
        vendas_df['Total'] = vendas_df['Total'].astype(float)
        vendas_df['Preço Unitário'] = vendas_df['Preço Unitário'].apply(lambda x: str(x).replace(',', '.'))
        vendas_df['Preço Unitário'] = vendas_df['Preço Unitário'].astype(float)
        vendas_df['Valor Substituição'] = vendas_df['Valor Substituição'].apply(lambda x: str(x).replace(',', '.'))
        vendas_df['Valor Substituição'] = vendas_df['Valor Substituição'].astype(float)
        # calculos da novas colunas
        vendas_df['CMV'] = vendas_df['Quantidade'] * vendas_df['Custo ICMS']
        vendas_df['Valor do IPI'] = vendas_df['IPI'] * vendas_df['Total'] / 100
        vendas_lojas = vendas_df.groupby('Nome Fantasia').sum()
        ano_referencia = vendas_df[-1:]['Ano da Venda'].item()
        mes_referencia = vendas_df[-1:]['Mes da Venda'].item()

        empresas = []
        codigo = []
        venda_bruta = []
        devolucao = []
        ipi= []
        cmv = []
        substituto = []

        for i, nome in enumerate(vendas_df['Nome Fantasia']):
            if nome in empresas:
                ind = empresas.index(nome)
                if vendas_df.loc[i, 'Total'] > 0:
                    venda_bruta[ind] += vendas_df.loc[i, 'Total']
                else:
                    devolucao[ind] += (vendas_df.loc[i, 'Total'] * -1)
                ipi[ind] += vendas_df.loc[i,'Valor do IPI']
                cmv[ind] += vendas_df.loc[i,'CMV']
                substituto[ind] += vendas_df.loc[i,'Valor Substituição']
            else:
                empresas.append(nome)
                codigo.append(vendas_df.loc[i, 'Empresa'])

                if vendas_df.loc[i, 'Total'] > 0:
                    venda_bruta.append(vendas_df.loc[i, 'Total'])
                    devolucao.append(0)
                else:
                    devolucao.append((vendas_df.loc[i, 'Total'] * -1))
                    venda_bruta.append(0)

                ipi.append(vendas_df.loc[i,'Valor do IPI'])
                cmv.append(vendas_df.loc[i,'CMV'])
                substituto.append(vendas_df.loc[i,'Valor Substituição'])

        # grava dados na empresa
        for i , cod in enumerate(codigo):

            ler_emp = Empresa.query.filter_by(id=int(cod)).first()

            if ler_emp:
                pass
            else:
                emp = Empresa(id=int(cod), nome=empresas[i])
                database.session.add(emp)
                database.session.commit()

        # grava dados do resultado por empresa

        emps = Empresa.query.all()
        total_receita = sum(venda_bruta)

        for emp in emps:
            ind = empresas.index(emp.nome)
            rep = venda_bruta[ind] / total_receita

            ler_despesas = EmpresaResultado.query.filter_by(id_empresa=emp.id,ano=ano_referencia,mes=mes_referencia).first()

            if ler_despesas:
                ler_despesas.receita_bruta=venda_bruta[ind]
                ler_despesas.devolucao=devolucao[ind]
                ler_despesas.rep_bruta=rep
                ler_despesas.cmv=cmv[ind]
                ler_despesas.icms_substituto=substituto[ind]
            else:
                resulta = EmpresaResultado(id_empresa=emp.id,ano=ano_referencia,mes=mes_referencia,\
                                           receita_bruta=venda_bruta[ind],devolucao=devolucao[ind],\
                                           rep_bruta=rep,ipi=ipi[ind],cmv=cmv[ind],icms_substituto=substituto[ind], \
                                           despesas_ven=0,despesas_ocu=0,despesas_adm=0,break_even=0,sup_caixa=0,\
                                           val_sup_caixa=0,per_imposto=0,val_imposto=0,despesas_rateadas=0,\
                                           tot_rec_liq=0,tot_cmv=0,lucro_bruto=0,rep_bruto=0,tot_adm=0,\
                                           rep_adm=0,rep_ven=0,tot_des=0,rep_des=0,ebit=0,rep_ebit=0,despesas_ger=0)

                database.session.add(resulta)
            database.session.commit()

        flash(f'Importação foi um sucesso', 'alert-success')

        return redirect(url_for('tela_principal'))
    return render_template('importar.html', form=form)

@app.route('/cria_conta', methods=['GET', 'POST'])
def cria_conta():
    form_criarconta = FormCriarConta()

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        return redirect(url_for('login'))
    return render_template('cria_conta.html', form_criarconta=form_criarconta)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    print(form_login.validate_on_submit())

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('tela_principal'))
        else:
            flash(f'Falha no Login. E-mail ou Senha Incorretos', 'alert-danger')

    return render_template('login.html', form_login=form_login)



@app.route('/sair')
@login_required
def sair():
    logout_user()
#    flash(f'Logout Feito com Sucesso', 'alert-success')
    return redirect(url_for('home'))

@app.route('/envia_excel/<resultado_id>', methods=['GET', 'POST'])
@login_required
def envia_excel(resultado_id):
    resultado = EmpresaResultado.query.get(resultado_id)

    if resultado:
        dicio_resulta = {}
        dicio_resulta['Referência'] = str(resultado.ano) + '/' + str(resultado.mes)
        dicio_resulta['Receita Bruta'] = formatacao(resultado.receita_bruta)
        dicio_resulta['Devolução de Vendas(-)'] = formatacao(resultado.devolucao)
        dicio_resulta['Impostos sobre Vendas(-)'] = formatacao(resultado.val_imposto)
        dicio_resulta['Receita Liquida(=)'] = formatacao(resultado.tot_rec_liq)
        dicio_resulta['Supri. Caixa(-)'] = formatacao(resultado.val_sup_caixa)
        dicio_resulta['Icms Substituto(-)'] = formatacao(resultado.icms_substituto)
        dicio_resulta['IPI(-)'] = formatacao(resultado.ipi)
        dicio_resulta['CMV(-)'] = formatacao(resultado.cmv)
        dicio_resulta['Total CMV(=)'] = formatacao(resultado.tot_cmv)
        dicio_resulta['Lucro Bruto(=)'] = formatacao(resultado.lucro_bruto)
        dicio_resulta['% Lucro Bruto'] = formatacao(resultado.rep_bruto)
        dicio_resulta['Despesas Adm Empresa(-)'] = formatacao(resultado.despesas_adm)
        dicio_resulta['Despesas Ocu Empresa(-)'] = formatacao(resultado.despesas_ocu)
        dicio_resulta['Despesas Rateadas(-)'] = formatacao(resultado.despesas_rateadas)
        dicio_resulta['Total de Despesas(=)'] = formatacao(resultado.tot_des)
        dicio_resulta['% Total de Despesas'] = formatacao(resultado.rep_des)
        dicio_resulta['Despesas Vendas(-)'] = formatacao(resultado.despesas_ven)
        dicio_resulta['% Despesas Vendas'] = formatacao(resultado.rep_ven)
        dicio_resulta['Total Administrativa(=)'] = formatacao(resultado.tot_adm)
        dicio_resulta['% Total Administrativa'] = formatacao(resultado.rep_adm)
        dicio_resulta['EBIT'] = formatacao(resultado.ebit)
        dicio_resulta['% EBIT'] = formatacao(resultado.rep_ebit)
        vendas_produtos_df = pd.DataFrame.from_dict(dicio_resulta, orient='index')
        vendas_produtos_df = vendas_produtos_df.rename(columns={0: resultado.resultado.nome})
        caminho = 'c:/planilhas'

        if not os.path.exists(caminho):
            os.makedirs(caminho)

        vendas_produtos_df.to_csv(caminho + '/Resultado.csv', sep=';', encoding='latin1')
        return redirect(url_for('tela_principal'))

@app.route('/compara_periodo/' , methods=['GET', 'POST'])
@login_required
def compara_periodo():
    form = FormComparaPeriodo()
    form.empresa.choices = [(g.id, g.nome) for g in Empresa.query.all()]

    if 'botao_submit' in request.form :

        per_inicial = str(form.int1_ano_ini.data) + '/' + str(form.int1_mes_ini.data) + ' até ' + \
                      str(form.int1_ano_fin.data) + '/' + str(form.int1_mes_fin.data)
        int1 = str(form.int1_ano_ini.data) + str(form.int1_mes_ini.data)
        int2 = str(form.int1_ano_fin.data) + str(form.int1_mes_fin.data)
        per_final = str(form.int2_ano_ini.data) + '/' + str(form.int2_mes_ini.data) + ' até ' + \
                    str(form.int2_ano_fin.data) + '/' + str(form.int2_mes_fin.data)
        int3 = str(form.int2_ano_ini.data) + str(form.int2_mes_ini.data)
        int4 = str(form.int2_ano_fin.data) + str(form.int2_mes_fin.data)
        # separa as empresas
        emp = []
        if form.todas_empresas.data:
            nome_empresa = 'TODAS AS EMPRESAS'
            empresa = Empresa.query.all()
            for i in empresa:
                emp.append(i.id)
        else:
            empresa = Empresa.query.get(form.empresa.data)
            if empresa:
                emp.append(empresa.id)
                nome_empresa = empresa.nome
        receita_bruta = [0,0,0]

        for i in emp:
            resultados = EmpresaResultado.query.filter_by(id_empresa=i)

            for resultado in resultados:
                if str(resultado.ano) + str(resultado.mes) >= int1 and \
                   str(resultado.ano) + str(resultado.mes) <= int2:
                   receita_bruta[0] += resultado.receita_bruta

                if str(resultado.ano) + str(resultado.mes) >= int3 and \
                   str(resultado.ano) + str(resultado.mes) <= int4:
                   receita_bruta[1] += resultado.receita_bruta

        if receita_bruta[0] > 0:
           receita_bruta[2] = (receita_bruta[0] - receita_bruta[1]) / receita_bruta[0]
        return render_template('mostra_comparacao.html', nome_empresa=nome_empresa, per_inicial=per_inicial,
                               per_final=per_final, receita_bruta=receita_bruta)

    return render_template('compara_periodo.html', form=form)



@app.route('/mostra_plano')
@login_required
def mostra_plano():
    planos = Plano.query.order_by(Plano.id)
    return render_template('mostra_plano.html', planos=planos)

@app.route('/edita_plano/<plano_id>' , methods=['GET', 'POST'])
@login_required
def edita_plano(plano_id):
    form = FormPlano()
    plano = Plano.query.get(plano_id)

    if 'botao_submit' in request.form:
        print(form.tipo.data.upper())
        plano.descricao = form.descricao.data
        plano.tipo = form.tipo.data.upper()
        database.session.commit()
        return redirect(url_for('mostra_plano'))

    form.id.data = plano.id
    form.descricao.data = plano.descricao
    form.tipo.data = plano.tipo
    form.opcao.data = 'A'
    return render_template('edita_plano.html', form=form)

@app.route('/incluir_plano', methods=['GET', 'POST'])
@login_required
def incluir_plano():
    form = FormPlano()

    if form.validate_on_submit():
        plano = Plano(id=form.id.data, descricao=form.descricao.data, tipo=form.tipo.data)
        database.session.add(plano)
        database.session.commit()
        return redirect(url_for('mostra_plano'))
    return render_template('edita_plano.html', form=form )

@app.route('/excluir_plano/<plano_id>', methods=['GET', 'POST'])
@login_required
def excluir_plano(plano_id):
    plano = Plano.query.get(plano_id)

    if plano:
        database.session.delete(plano)
        database.session.commit()
        return redirect(url_for('mostra_plano'))
    else:
        abort(403)

@app.route('/importar_despesas' , methods=['GET', 'POST'])
@login_required
def importar_despesas():
    form = FormImportarDespesas()

    if form.validate_on_submit():
        caminho_despesas = salvar_arquivo(form.despesas.data)
        despesas_df = pd.read_csv(caminho_despesas, sep=';', encoding='latin1')
        pagar_df = despesas_df[despesas_df['Receber / Pagar'] == 'Pagar']
        pagar_df['Data de Emissão'] = pd.to_datetime(pagar_df['Data de Emissão'], format='%d/%m/%Y')
        pagar_df['Ano da despesa'] = pagar_df['Data de Emissão'].dt.year
        pagar_df['Mes da despesa'] = pagar_df['Data de Emissão'].dt.month

        # converte valores em numerico
        pagar_df['Valor Total R$'] = pagar_df['Valor Total R$'].apply(lambda x: str(x).replace(',', '.'))
        pagar_df['Valor Total R$'] = pagar_df['Valor Total R$'].astype(float)
        pagar_df['Tipo'] = ''
        # ano e mes de referencia
        ano_referencia = pagar_df[-1:]['Ano da despesa'].item()
        mes_referencia = pagar_df[-1:]['Mes da despesa'].item()
        # sepera por empresa
        empresa_des = {} # adm , ocu , ven , imp , ger
        geral_des = [0,0,0,0] # adm , ocu , pro , ger
        despesa_erro = {}
        empresa = Empresa.query.all()
        tab_emp = []
        for i in empresa:
            tab_emp.append(i.id)

        for lin , codigo in enumerate(pagar_df['Cod Empresa']):
            # teste se a empresa é valida
            cod_emp = 10

            if codigo in tab_emp:
                cod_emp = tab_emp[tab_emp.index(codigo)]

            plano = Plano.query.get(int(pagar_df.loc[lin, 'Código Histórico']))

            if plano :
                pagar_df.loc[lin,'Tipo'] = plano.tipo

                if plano.tipo == 'EXC':
                    continue
                # conta rateada geral
                if 'FILIAL' in str(pagar_df.loc[lin, 'Observação']).upper():
                    if plano.tipo == 'ADM':
                        geral_des[0] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo == 'OCU':
                        geral_des[1] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo == 'PRO':
                        geral_des[2] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo != 'ADM' and plano.tipo != 'OCU' and plano.tipo != 'PRO':
                        geral_des[3] += pagar_df.loc[lin,'Valor Total R$']
                else:
            # conta rateada empresa
                    if cod_emp not in empresa_des:
                        empresa_des[cod_emp] = [0,0,0,0,0]
                    if plano.tipo == 'ADM':
                        empresa_des[cod_emp][0] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo == 'OCU':
                        empresa_des[cod_emp][1] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo == 'VEN':
                        empresa_des[cod_emp][2] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo == 'IMP':
                        empresa_des[cod_emp][3] += pagar_df.loc[lin,'Valor Total R$']
                    if plano.tipo != 'ADM' and plano.tipo != 'OCU' and plano.tipo != 'VEN' and plano.tipo != 'IMP':
                        empresa_des[cod_emp][4] += pagar_df.loc[lin,'Valor Total R$']
            else:
                # grava erro no movimento
                despesa_erro[pagar_df.loc[lin ,'Histórico'] + str(pagar_df.loc[lin, 'Código Histórico'])] = pagar_df.loc[lin , 'Valor Total R$']
        # grava na planilha para verificao
        caminho = 'c:/planilhas'

        if not os.path.exists(caminho):
            os.makedirs(caminho)

        pagar_df.to_csv(caminho + '/Despesa.csv', sep=';', encoding='latin1')
        # grava na despesas gerais

        if not despesa_erro:
            # grava despesas gerais
            despesa = DespesasRateadas.query.filter_by(ano=ano_referencia,mes=mes_referencia).first()

            if despesa:
                despesa.despesas_adm = geral_des[0]
                despesa.despesas_ocu = geral_des[1]
                despesa.despesas_pro = geral_des[2]
                despesa.despesas_ger = geral_des[3]
            else:
                despesa = DespesasRateadas(ano=ano_referencia, mes=mes_referencia, despesas_pro=geral_des[2],
                                           despesas_adm=geral_des[0], despesas_ocu=geral_des[1],
                                           despesas_ger=geral_des[3])
                database.session.add(despesa)

            database.session.commit()
            # grava despesa por empresa
            for emp in empresa_des:
                resultado = EmpresaResultado.query.filter_by(id_empresa=emp,ano=ano_referencia,mes=mes_referencia).first()

                if resultado:
                    resultado.despesas_adm = empresa_des[emp][0]
                    resultado.despesas_ocu = empresa_des[emp][1]
                    resultado.despesas_ven = empresa_des[emp][2]
                    resultado.val_imposto = empresa_des[emp][3]
                    resultado.despesas_ger = empresa_des[emp][4]
                else:
                    resulta = EmpresaResultado(id_empresa=emp, ano=ano_referencia, mes=mes_referencia, \
                                               receita_bruta=0, devolucao=0, rep_bruta=0, ipi=0, cmv=0,
                                               icms_substituto=0, despesas_ven=empresa_des[emp][2], \
                                               despesas_ocu=empresa_des[emp][1], despesas_adm=empresa_des[emp][0], \
                                               break_even=0,sup_caixa=0, \
                                               val_sup_caixa=0, per_imposto=0, val_imposto=empresa_des[emp][3], despesas_rateadas=0, \
                                               tot_rec_liq=0, tot_cmv=0, lucro_bruto=0, rep_bruto=0, tot_adm=0, \
                                               rep_adm=0, rep_ven=0, tot_des=0, rep_des=0, ebit=0, rep_ebit=0,
                                               despesas_ger=empresa_des[emp][4])

                    database.session.add(resulta)
                database.session.commit()

        return render_template('mostra_importacao_despesas.html', empresa_des=empresa_des, geral_des=geral_des, despesa_erro=despesa_erro)
    return render_template('importar_despesas.html', form=form)
