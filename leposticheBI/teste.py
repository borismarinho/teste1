from flask import render_template, redirect, url_for, flash, request, abort
from leposticheBI import app, database, bcrypt
from leposticheBI.forms import FormLogin, FormCriarConta, FormDespesasGerais, FormEmpresas, FormDespesasEmpresa, FormImportar, FormFechaPeriodo, FormComparaPeriodo, FormPlano
from leposticheBI.models import Usuario, Empresa , EmpresaResultado, DespesasRateadas, Plano , EmpresaResultado
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import func

caminho_plano = 'C:/Users/Dickerson/Downloads/plano.xlsx'
plano_df = pd.read_excel(caminho_plano)

for i, codigo in enumerate(plano_df['Codigo']):
    plano = Plano(id=codigo, descricao=plano_df.loc[i, 'Nome'], tipo=plano_df.loc[i, 'Tipo'][:3].upper())
    database.session.add(plano)
    database.session.commit()





