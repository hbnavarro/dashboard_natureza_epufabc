# %%
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from streamlit_plotly_events import plotly_events

import sys
import os

# --- LÓGICA DE IMPORTAÇÃO (BOILERPLATE) ---
# Adiciona o diretório raiz ao caminho do Python para conseguir importar o utils.py
diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(diretorio_raiz)

# Agora podemos importar a função
from utils import carregar_dados, menu_lateral # Importa também o menu_lateral

st.set_page_config(
    page_title="Física no ENEM",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded")

menu_lateral() # <--- Adicione aqui também

# --- CÓDIGO DA PÁGINA ---

st.title("⚛️ Física ENEM")

#alt.theme.enable("dark")
alt.theme.enable("ggplot2")# estilo ggplot2

# Mapeamento fixo de cores
cores_tipo_questao = {
    "Conta": "#0c3d0e",       # Verde Escuro (Sua cor preferida)
    "Conceitual": "#f5ac19",  # Laranja (A terceira cor da sua lista anterior)
    # Adicionei a cor vermelha da sua lista caso exista uma terceira categoria ou erro
    "Mista": "#ed3d00",       
    "(?)": "#ed3d00"
}

try:
    # AQUI ESTÁ A MÁGICA:
    # Certifique-se que no seu Google Sheets a aba se chama EXATAMENTE "Fisica"
    df = carregar_dados(nome_da_aba="Fisica") 
    
    # ==============================================================================
    # 1. BARRA LATERAL (FILTROS)
    # ==============================================================================
    st.sidebar.header("Filtros Globais")
    anos_disponiveis = sorted(df["Ano"].unique())

    ano_inicio, ano_fim = st.sidebar.selectbox("Ano inicial", anos_disponiveis), \
                        st.sidebar.selectbox("Ano final", anos_disponiveis)

    if ano_inicio > ano_fim:
        st.sidebar.error("O ano inicial deve ser menor ou igual ao ano final.")

    df_filtered = df[(df["Ano"] >= ano_inicio) & (df["Ano"] <= ano_fim)]

    # ==============================================================================
    # 2. SEÇÃO DE KPIS (RESUMO EXECUTIVO - PORCENTAGENS + TOTAL)
    # ==============================================================================

    # 1. Totalizador
    total_questoes = df_filtered.shape[0]

    if total_questoes > 0:
        # --- Cálculo Mecânica ---
        qtd_mec = df_filtered[df_filtered["Frente"] == "Mecânica"].shape[0]
        pct_mec = (qtd_mec / total_questoes) * 100

        # --- Cálculo Eletromagnetismo ---
        qtd_eletro = df_filtered[df_filtered["Frente"] == "Eletromagnetismo"].shape[0]
        pct_eletro = (qtd_eletro / total_questoes) * 100

        # --- Cálculo Combo (Termo + Ondulatória + Óptica) ---
        grupo_fisica_classica = ["Termofísica", "Ondulatória", "Óptica"]
        qtd_combo = df_filtered[df_filtered["Frente"].isin(grupo_fisica_classica)].shape[0]
        pct_combo = (qtd_combo / total_questoes) * 100
    else:
        pct_mec = pct_eletro = pct_combo = 0.0

    # 2. Visualização (Container com 4 colunas)
    with st.container(border=True):
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        col_kpi1.metric("Mecânica", f"{pct_mec:.1f}%")
        col_kpi2.metric("Eletromagnetismo", f"{pct_eletro:.1f}%")
        col_kpi3.metric("Termo / Ondul. / Óptica", f"{pct_combo:.1f}%")
        
        # Coluna nova
        col_kpi4.metric("Total de Questões", f"{total_questoes}")

    st.markdown("---")


    st.markdown("## 🌎 Visão Geral")

    # Processamento dos dados
    contagem_frentes = df_filtered["Frente"].value_counts().reset_index()
    contagem_frentes.columns = ["Frente", "Quantidade"]

    with st.container(border=True):
        colA, colB = st.columns([2, 1])

        # --- GRÁFICO DE BARRAS (ESQUERDA) ---
        with colA:
            fig1 = px.bar(
                contagem_frentes,
                x="Frente",
                y="Quantidade",
                text="Quantidade",
                title="Volume de Questões por Frente",
                color="Quantidade",              # Gradiente baseado no valor
                color_continuous_scale="Greens"  # Paleta Verde
            )
            # Limpeza visual (Clean Academic Style)
            fig1.update_layout(
                xaxis_title=None, # Remove título redundante
                yaxis_title=None,
                coloraxis_showscale=False, # Remove barra de cores lateral
                paper_bgcolor="rgba(0,0,0,0)", # Fundo transparente para integrar com o container
                plot_bgcolor="rgba(0,0,0,0)",
            )
            fig1.update_traces(textposition="outside")
            st.plotly_chart(fig1, width='stretch')

        # --- GRÁFICO DE PIZZA (DIREITA) ---
        with colB:
            fig_pizza = px.pie(
                contagem_frentes,
                names="Frente",
                values="Quantidade",
                title="Proporção",
                hole=0.4,
                # Usando tons de verde discretos (reverse para começar escuro)
                color_discrete_sequence=['#0c3d0e', '#ed3d00', '#f5ac19']
            )
            fig_pizza.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", # Fundo transparente
                showlegend=False, # Opcional: remover legenda se houver pouco espaço
                #margin=dict(t=40, b=0, l=0, r=0)
            )
            fig_pizza.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_pizza, width='stretch')

    # ===== Linha 2 ===== #

    # ===== GRÁFICO 2: Proporção de questões Conceituais vs Conta =====

    #with st.container(border=True):

    col1, col2 = st.columns(2)

    contagem_tipos = df_filtered["Tipo"].value_counts().reset_index()
    contagem_tipos.columns = ["Tipo", "Quantidade"]

    fig2 = px.pie(
        contagem_tipos,
        names="Tipo",
        values="Quantidade",
        title="Distribuição de tipos de questão (Conceitual vs Conta)",
        hole=0.4,
        # --- MUDANÇA AQUI ---
        color="Tipo",                     # Diz qual coluna contém "Conta" ou "Conceitual"
        color_discrete_map=cores_tipo_questao  # Aplica o dicionário fixo
    )

    with col1:
        with st.container(border=True, height=500):
            st.plotly_chart(fig2, width='stretch')


    # ===== GRÁFICO 3: Tópicos mais cobrados (Plotly, com gradiente) =====

    import plotly.graph_objects as go  # <-- certifique-se de ter esta importação no topo do script

    # preparar os dados
    contagem_topicos = (
        df_filtered["Tópico"]
        .value_counts()
        .reset_index(name="Quantidade")
    )
    contagem_topicos.columns = ["Tópico", "Quantidade"]

    # ordenar do maior para o menor (queremos os maiores no topo)
    contagem_topicos = contagem_topicos.sort_values("Quantidade", ascending=False).reset_index(drop=True)

    # normalizar para escala visual das barras (0..1)

    contagem_topicos["Porcentagem"] = contagem_topicos["Quantidade"] / contagem_topicos["Quantidade"].max()

    # construir a figura
    fig_topicos = go.Figure()
    fig_topicos.add_trace(
        go.Bar(
            x=contagem_topicos["Porcentagem"],     # comprimento da barra (normalizado)
            y=contagem_topicos["Tópico"],
            orientation="h",
            marker=dict(
                color=contagem_topicos["Quantidade"],  # cor baseada na quantidade -> gradiente
                colorscale="Greens",
                showscale=False
            ),
            text=contagem_topicos["Quantidade"],    # valor numérico mostrado
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Questões: %{text}<extra></extra>",
        )
    )

    # layout e estilo

    fig_topicos.update_layout(
        title="Tópicos mais cobrados",
        xaxis=dict(visible=False),
        yaxis=dict(autorange="reversed", title=""),  # autorange reversed para manter maiores no topo
        height=500
        #margin=dict(l=140, r=40, t=60, b=20)

    )


    # desenhar no col3

    with col2:
        with st.container(border=True, height=500):
            st.plotly_chart(fig_topicos, width='stretch')

    #col2.plotly_chart(fig_topicos, width='stretch')


    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------

    st.subheader("📈 Evolução da Cobrança por Frente ao Longo dos Anos")

    # corrigir frentes
    frentes_evolucao = (
        df["Frente"]
        .dropna()
        .astype(str)
        .unique()
    )
    frentes_evolucao = sorted(frentes_evolucao)

    frentes_escolhidas_evolucao = st.multiselect(
        "Selecione as frentes para visualizar a evolução:",
        frentes_evolucao,
        default=frentes_evolucao
    )

    # Filtrar apenas pelo intervalo de ano
    df_evo = df[(df["Ano"] >= ano_inicio) & (df["Ano"] <= ano_fim)]

    # Garantir que só filtra por frente aqui (não na visão geral)
    if frentes_escolhidas_evolucao:
        df_evo = df_evo[df_evo["Frente"].isin(frentes_escolhidas_evolucao)]

    # ==============================
    # 1. Lista completa de anos no intervalo
    # ==============================
    anos_completos = list(range(ano_inicio, ano_fim + 1))

    # ==============================
    # 2. Criar todas as combinações Ano × Frente
    # ==============================
    import itertools

    frentes_usadas = sorted(df_evo["Frente"].unique())

    combinacoes = pd.DataFrame(
        list(itertools.product(anos_completos, frentes_usadas)),
        columns=["Ano", "Frente"]
    )

    # ==============================
    # 3. Contar questões reais e preencher ausentes com zero
    # ==============================
    evo_real = (
        df_evo.groupby(["Ano", "Frente"])
        .size()
        .reset_index(name="Quantidade")
    )

    # Merge completo
    evolucao_frentes = combinacoes.merge(
        evo_real,
        on=["Ano", "Frente"],
        how="left"
    ).fillna({"Quantidade": 0})

    # Garantir tipo numérico
    evolucao_frentes["Quantidade"] = evolucao_frentes["Quantidade"].astype(int)

    # ==============================
    # 4. Gráfico de evolução (Altair)
    # ==============================

    # Sua paleta personalizada
    #cores_personalizadas = ['#0c3d0e', '#ed3d00', '#f5ac19']

    grafico_evolucao = (
        alt.Chart(evolucao_frentes)
        .mark_line(point=True)
        .encode(
            x=alt.X("Ano:O", sort="ascending", title="Ano"),
            y=alt.Y("Quantidade:Q", title="Número de Questões", scale=alt.Scale(domainMin=0)),
            
            # --- MUDANÇA AQUI ---
            color=alt.Color("Frente:N", scale=alt.Scale(scheme='tableau10')),
            # --------------------

            tooltip=[
                alt.Tooltip("Ano:O"),
                alt.Tooltip("Frente:N"),
                alt.Tooltip("Quantidade:Q", title="Questões")
            ]
        )
        .properties(
            width=600,
            height=400
        )
        .interactive()
    )

    # Nota: O parâmetro correto moderno no Streamlit é use_container_width=True
    st.altair_chart(grafico_evolucao, width='stretch')

    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------

    st.markdown("## 🔎 Análise detalhada por Frente")

    # Filtro independente, respeitando o filtro de Ano
    frentes_detalhe = sorted(df_filtered["Frente"].unique())

    frente_escolhida = st.selectbox(
        "Selecione uma Frente para análise detalhada:",
        frentes_detalhe
    )

    # Filtrar pelo conjunto já filtrado por Ano + Frente
    df_detalhado = df_filtered[df_filtered["Frente"] == frente_escolhida]

    # Criar três colunas
    colA, colB = st.columns(2)

    # ====================== GRÁFICO 1: Tópicos ======================
    contagem_topicos = (
        df_detalhado["Tópico"]
        .value_counts()
        .reset_index()
    )
    contagem_topicos.columns = ["Tópico", "Quantidade"]

    fig3 = px.bar(
        contagem_topicos,
        x="Tópico",
        y="Quantidade",
        title=f"Quantidade de questões por tópico — Frente: {frente_escolhida}",
        text="Quantidade",
        color="Quantidade",
        color_continuous_scale="Greens"
    )

    fig3.update_layout(xaxis_title="Tópico", yaxis_title="Quantidade")
    fig3.update_traces(textposition="outside")

    with colA:
        with st.container(border=True):
            st.plotly_chart(fig3, width='content')

    # ====================== TABELA DE SUBTÓPICOS (COM FILTRO DE TÓPICO) ======================

    # 1) Selecionar Tópico para filtrar a tabela
    topicos_disponiveis = ["Todos os tópicos"] + sorted(df_detalhado["Tópico"].dropna().unique())

    topico_filtro = colB.selectbox(
        "Filtrar tabela por Tópico:",
        topicos_disponiveis
    )

    # 2) Preparar subtópicos como antes
    sub1 = df_detalhado[["Tópico", "Subtópico 1"]].dropna(subset=["Subtópico 1"])
    sub2 = df_detalhado[["Tópico", "Subtópico 2"]].dropna(subset=["Subtópico 2"])

    sub1 = sub1.rename(columns={"Subtópico 1": "Conteúdo"})
    sub2 = sub2.rename(columns={"Subtópico 2": "Conteúdo"})

    tabela_subs = pd.concat([sub1, sub2], ignore_index=True)

    # 3) Aplicar filtro pelo Tópico
    if topico_filtro != "Todos os tópicos":
        tabela_subs = tabela_subs[tabela_subs["Tópico"] == topico_filtro]

    # 4) Agrupar por Subtópico + Tópico
    tabela_final = (
        tabela_subs.groupby(["Conteúdo", "Tópico"])
        .size()
        .reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=False)
    )

    # 6) Mostrar tabela
    colB.dataframe(
        tabela_final,
        width='stretch',
        hide_index=True
    )


    #======================= SEGUNDA PARTE =======================================

    colC, colD = st.columns(2) 


    # ====================== GRÁFICO 3: Evolução temporal por tópico ======================

    # 1) Filtrar apenas os anos disponíveis dentro do filtro global
    anos_validos = sorted(df_detalhado["Ano"].unique())

    # 2) Criar uma tabela completa Ano × Tópico garantindo zero onde não há questões
    tabela = (
        df_detalhado.groupby(["Ano", "Tópico"])
        .size()
        .reset_index(name="Quantidade")
    )

    # Criar todos os pares possíveis Ano x Tópico
    anos = df_detalhado["Ano"].unique()
    topicos = df_detalhado["Tópico"].unique()

    multi_index = pd.MultiIndex.from_product(
        [anos, topicos], names=["Ano", "Tópico"]
    )

    tabela_completa = (
        tabela.set_index(["Ano", "Tópico"])
        .reindex(multi_index, fill_value=0)
        .reset_index()
    )

    # Ordenar por ano para o gráfico ficar correto
    tabela_completa = tabela_completa.sort_values("Ano")

    # 3) Criar o gráfico de linhas com Plotly
    fig_evolucao = px.line(
        tabela_completa,
        x="Ano",
        y="Quantidade",
        #color="Tópico",
        markers=True,
        title=f"Evolução temporal dos tópicos — Frente: {frente_escolhida}",
        color="Quantidade",
        color_discrete_sequence=px.colors.sequential.Greens_r
    )


    fig_evolucao.update_layout(
        xaxis_title="Ano",
        yaxis_title="Quantidade de Questões",
        legend_title="Tópico",
    )

    #colC.plotly_chart(fig_evolucao, width='stretch')


    # ====================== GRÁFICO 3: Conceitual vs Conta ======================
    contagem_tipos = (
        df_detalhado["Tipo"]
        .value_counts()
        .reset_index()
    )
    contagem_tipos.columns = ["Tipo", "Quantidade"]

    fig5 = px.pie(
        contagem_tipos,
        names="Tipo",
        values="Quantidade",
        title=f"Distribuição de tipos — {frente_escolhida}",
        hole=0.4,
        # --- MUDANÇA AQUI ---
        color="Tipo",                     # Diz qual coluna contém "Conta" ou "Conceitual"
        color_discrete_map=cores_tipo_questao  # Aplica o dicionário fixo
    )

    with colC:
        with st.container(border=True, height=450):
            st.plotly_chart(fig5, width='content')


    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------


    # ====================== GRÁFICO: Heatmap Tópico × Ano ======================

    df_temp = df_detalhado.copy()

    # Seleciona apenas o ano e o tópico
    df_temp = df_temp[["Ano", "Tópico"]].dropna()

    # Conta quantas questões ocorreram para cada (Ano, Tópico)
    contagem = df_temp.groupby(["Ano", "Tópico"]).size().reset_index(name="Quantidade")

    # Pivot para formato matricial
    tabela_heatmap = contagem.pivot_table(
        index="Tópico",
        columns="Ano",
        values="Quantidade",
        fill_value=0
    )

    # Ordena anos (colunas)
    tabela_heatmap = tabela_heatmap.sort_index(axis=1)

    # Cria o Heatmap
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=tabela_heatmap.values,
            x=tabela_heatmap.columns,
            y=tabela_heatmap.index,
            colorscale="Greens",
            colorbar=dict(title="Qtd.")
        )
    )

    fig_heat.update_layout(
        title=f"Mapa de Calor — Questões por Tópico e Ano ({frente_escolhida})",
        xaxis_title="Ano",
        yaxis_title="Tópico",
        #height=500
    )

    with colD:
        with st.container(border=True, height=450):
            st.plotly_chart(fig_heat, width='stretch')

    # ... (Seu código anterior termina aqui, após o container do Heatmap)

    # ==============================================================================
    # NOVA SEÇÃO: ANÁLISE PROFUNDA DE CONTEÚDO (SUBTÓPICOS)
    # ==============================================================================

    st.markdown("---") # Separador visual
    st.subheader(f"🔬 Análise Específica: Conteúdos de {frente_escolhida}")

    # 1. Filtro de Tópico (Específico para esta seção)
    # Pegamos os tópicos únicos do dataframe que já foi filtrado por Frente e Ano
    lista_topicos_filtrada = sorted(df_detalhado["Tópico"].dropna().unique())

    if lista_topicos_filtrada:
        topico_selecionado = st.selectbox(
            "Selecione um Tópico para ver os conteúdos mais cobrados:",
            lista_topicos_filtrada
        )

        # Criação de um novo DataFrame isolado para não afetar o resto do dashboard
        df_analise_topico = df_detalhado[df_detalhado["Tópico"] == topico_selecionado]

        # --- PREPARAÇÃO DOS DADOS: SUBTÓPICOS ---
        # Unifica Subtópico 1 e 2 numa única lista para contagem total
        subs1 = df_analise_topico["Subtópico 1"].dropna()
        subs2 = df_analise_topico["Subtópico 2"].dropna()
        
        todos_subs = pd.concat([subs1, subs2])
        
        contagem_subs = todos_subs.value_counts().reset_index()
        contagem_subs.columns = ["Subtópico", "Quantidade"]
        
        # Ordenar decrescente
        contagem_subs = contagem_subs.sort_values("Quantidade", ascending=True) # Ascendente para barra horizontal ficar certa (maior no topo)

        # --- PREPARAÇÃO DOS DADOS: TIPO (CONTA vs CONCEITUAL) ---
        contagem_tipo_topico = df_analise_topico["Tipo"].value_counts().reset_index()
        contagem_tipo_topico.columns = ["Tipo", "Quantidade"]

        # --- VISUALIZAÇÃO ---
        col_sub1, col_sub2 = st.columns([2, 1]) # Coluna da esquerda maior para as barras

        # Gráfico de Barras (Conteúdos)
        with col_sub1:
            # Altura dinâmica: Se tiver muitos subtópicos, aumenta o gráfico
            altura_grafico = max(400, len(contagem_subs) * 40)
            
            fig_subs = px.bar(
                contagem_subs,
                x="Quantidade",
                y="Subtópico",
                orientation='h', # Horizontal facilita a leitura de nomes longos de subtópicos
                title=f"Conteúdos mais cobrados em {topico_selecionado}",
                text="Quantidade",
                color="Quantidade",
                color_continuous_scale="Greens"
            )
            
            fig_subs.update_layout(
                height=altura_grafico,
                xaxis_title=None,
                yaxis_title=None,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            fig_subs.update_traces(textposition="outside")

            with st.container(border=True, height=500):
                st.plotly_chart(fig_subs, width='content')

        # Gráfico de Pizza (Tipo)
        with col_sub2:
            fig_tipo_topico = px.pie(
                contagem_tipo_topico,
                names="Tipo",
                values="Quantidade",
                title=f"Perfil das questões ({topico_selecionado})",
                hole=0.4,
                # Mantendo a paleta personalizada que você gostou
                # --- MUDANÇA AQUI ---
                color="Tipo",                     # Diz qual coluna contém "Conta" ou "Conceitual"
                color_discrete_map=cores_tipo_questao  # Aplica o dicionário fixo
            )
            
            fig_tipo_topico.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=-0.1) # Legenda embaixo para economizar espaço lateral
            )

            with st.container(border=True, height=500):
                st.plotly_chart(fig_tipo_topico, width='content')

    else:
        st.warning("Não há dados de tópicos para o filtro selecionado.")



except Exception as e:
    st.error(f"Erro ao carregar dados da aba Física: {e}")



#df = pd.read_csv("Base de dados - ENEM EPUFABC.csv", sep=",")


