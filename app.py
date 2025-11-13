import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
import numpy as np

# --- Importação da lógica do usuário ---
try:
    from src.solver_bb_updated import solve_knapsack_bb_updated
except ImportError:
    st.error("Erro: Não foi possível encontrar 'src/solver_bb_updated.py'.")
    st.stop()

st.set_page_config(layout="wide")
st.title("Projeto de Pesquisa Operacional - Otimizador de Estações (Knapsack)")

# --- Carregamento de Dados ---
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        df = df[df['Peso'] > 0]
        df['Ratio'] = df['Valor'] / df['Peso']
        return df
    except FileNotFoundError:
        st.error(f"Erro: Arquivo {path} não encontrado.")
        return None

caminho_knapsack_data = os.path.join(r".\data\processed", 'knapsack_data.csv')
df_knapsack = load_data(caminho_knapsack_data)
if df_knapsack is None:
    st.stop()

# --- Heurística Gulosa ---
@st.cache_data
def solve_greedy(df_items, W):
    items = []
    for _, row in df_items.iterrows():
        if row['Peso'] <= W and row['Peso'] > 0:
            items.append((row['Station'], row['Valor'], row['Peso'], row['Ratio']))
    items.sort(key=lambda x: x[3], reverse=True)
    total_value = 0.0
    total_weight = 0.0
    selected_items = []
    for item in items:
        if total_weight + item[2] <= W:
            total_weight += item[2]
            total_value += item[1]
            selected_items.append(item[0])
    return total_value, total_weight, selected_items

# --- Sidebar ---
st.sidebar.header("1. Controles de Execução")

total_weight_available = df_knapsack['Peso'].sum()
default_w = total_weight_available * 0.20

W_CAPACITY = st.sidebar.number_input(
    "Orçamento (Capacidade W):", min_value=0.0, value=default_w, step=1000.0, format="%.2f", key="widget_w")
TIME_LIMIT = st.sidebar.number_input(
    "Limite de Tempo (s):", min_value=1, value=30, step=1, key="widget_time")
MAX_NODES = st.sidebar.number_input(
    "Limite de Nós (milhões):", min_value=1.0, value=50.0, step=1.0, format="%.1f", key="widget_nodes")
MAX_NODES_LIMIT = int(MAX_NODES * 1_000_000)

# Navegação
st.sidebar.header("2. Navegação")
page = st.sidebar.radio("Selecione a Página:",
                        ["Análise de Dados (EDA)", "Execução e Resultados", "Análise de Sensibilidade"])

if 'results' not in st.session_state:
    st.session_state.results = None

# ==========================================================
# 4.2 DASHBOARD DE ANÁLISE DE DADOS (COM FILTROS)
# ==========================================================
if page == "Análise de Dados (EDA)":
    st.header("4.2 Dashboard de Análise de Dados")

    st.subheader("Filtros Interativos")
    val_min, val_max = st.slider("Faixa de Valor", float(df_knapsack['Valor'].min()), float(df_knapsack['Valor'].max()),
                                 (float(df_knapsack['Valor'].min()), float(df_knapsack['Valor'].max())))
    peso_min, peso_max = st.slider("Faixa de Peso", float(df_knapsack['Peso'].min()), float(df_knapsack['Peso'].max()),
                                   (float(df_knapsack['Peso'].min()), float(df_knapsack['Peso'].max())))

    df_filtered = df_knapsack[(df_knapsack['Valor'].between(val_min, val_max)) &
                              (df_knapsack['Peso'].between(peso_min, peso_max))]

    st.write(f"Mostrando {len(df_filtered)} de {len(df_knapsack)} itens filtrados.")

    st.subheader("Estatísticas Descritivas (Filtradas)")
    st.write(df_filtered[['Valor', 'Peso', 'Ratio']].describe())

    st.subheader("Distribuições e Relações")
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))
    sns.histplot(df_filtered['Valor'], kde=True, ax=ax[0], color='blue')
    ax[0].set_title("Distribuição de Valor")
    sns.histplot(df_filtered['Peso'], kde=True, ax=ax[1], color='red')
    ax[1].set_title("Distribuição de Peso")
    sns.scatterplot(df_filtered, x="Peso", y="Valor", hue="Ratio", ax=ax[2])
    ax[2].set_title("Peso vs Valor (Cor = Ratio)")
    st.pyplot(fig)

    st.subheader("Tabela de Dados Filtrada")
    st.data_editor(df_filtered)

# ==========================================================
# 4.3 + 4.4 DASHBOARD DO ALGORITMO E RESULTADOS
# ==========================================================
elif page == "Execução e Resultados":
    st.header("4.3 Dashboard do Algoritmo e 4.4 Resultados")

    run = st.button("Executar Branch and Bound")
    if run:
        progress_chart = st.empty()
        progresso_valores = []
        placeholders = None

        start_time = time.time()
        results = solve_knapsack_bb_updated(
            df_knapsack,
            W_CAPACITY,
            TIME_LIMIT,
            MAX_NODES_LIMIT,
            placeholders
        )

        st.session_state.results = results
        end_time = time.time()
        exec_time = end_time - start_time

    if st.session_state.results:
        res = st.session_state.results
        st.success(f"Status: {res['status']}")
        cols = st.columns(4)
        cols[0].metric("Valor Máx (Z)", f"{res['max_value']:.2f}")
        cols[1].metric("Peso Total", f"{res['final_weight']:.2f}")
        cols[2].metric("Nós Expandidos", f"{res['nodes_expanded']:,}")
        cols[3].metric("Tempo (s)", f"{res['exec_time']:.2f}")

        greedy_val, greedy_weight, _ = solve_greedy(df_knapsack, W_CAPACITY)
        delta = res['max_value'] - greedy_val

        st.subheader("Comparação com Heurística Gulosa")
        st.metric("Valor Guloso", f"{greedy_val:.2f}")
        if delta > 0:
            st.success(f"B&B foi {delta:.2f} melhor que a heurística.")
        else:
            st.warning("Heurística obteve valor similar ou melhor (tempo limite pode ter sido atingido).")

        st.subheader("Itens Selecionados")
        df_sol = df_knapsack[df_knapsack['Station'].isin(res['final_solution_items'])]
        st.dataframe(df_sol[['Station', 'Valor', 'Peso', 'Ratio']])

# ==========================================================
# 5.2 ANÁLISE DE SENSIBILIDADE E ROBUSTEZ
# ==========================================================
elif page == "Análise de Sensibilidade":
    st.header("5.2 Análise de Sensibilidade e Robustez")

    st.write("Avalie o impacto da variação da capacidade W sobre o valor final.")
    percentuais = st.multiselect("Selecione percentuais da capacidade total:",
                                 [10, 20, 30, 40, 50, 75, 100, 125, 150],
                                 default=[50, 100, 150])

    resultados = []
    for p in percentuais:
        w_test = total_weight_available * (p / 100)
        res = solve_knapsack_bb_updated(df_knapsack, w_test, 10, 5_000_000)
        resultados.append({"Capacidade %": p, "Valor Ótimo": res["max_value"], "Peso Total": res["final_weight"]})

    df_sens = pd.DataFrame(resultados)
    st.subheader("Resultados da Sensibilidade")
    st.dataframe(df_sens)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(df_sens, x="Capacidade %", y="Valor Ótimo", marker="o", ax=ax)
    ax.set_title("Variação do Valor Ótimo conforme a Capacidade")
    ax.set_xlabel("% da Capacidade Total")
    ax.set_ylabel("Valor Ótimo (Z)")
    st.pyplot(fig)
