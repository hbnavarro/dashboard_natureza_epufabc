# %%
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt

import sys
import os

# --- LÓGICA DE IMPORTAÇÃO (BOILERPLATE) ---
# Adiciona o diretório raiz ao caminho do Python para conseguir importar o utils.py
diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(diretorio_raiz)

# Agora podemos importar a função
from utils import carregar_dados, menu_lateral # Importa também o menu_lateral


# --- CÓDIGO DA PÁGINA ---
st.set_page_config(
    page_title="Biologia ENEM",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded")

menu_lateral() # <--- Adicione aqui também


st.title("🧬 Biologia ENEM")

#alt.theme.enable("dark")
alt.theme.enable("ggplot2")# estilo ggplot2

