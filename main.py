import pandas as pd
import os

# Importações do projeto
from src.data_processing import carregar_e_limpar_dados
from src.solver_bb import solve_knapsack_bb

# --- 1. PROCESSAMENTO DE DADOS ---
print("--- 1. PROCESSAMENTO INICIAL ---")
pasta_raw = r".\data\raw"
pasta_processed = r".\data\processed"
dados = carregar_e_limpar_dados(pasta_raw, pasta_processed)

# --- 1.4 ANÁLISE EXPLORATÓRIA (EDA) E PREPARAÇÃO ---
print("\n--- 1.4 ANÁLISE EXPLORATÓRIA (EDA) ---")

print("Carregando dados preparados para o Knapsack...")
caminho_knapsack_data = os.path.join(pasta_processed, 'knapsack_data.csv')

try:
    df_knapsack = pd.read_csv(caminho_knapsack_data)
except FileNotFoundError:
    print(f"Erro: Arquivo {caminho_knapsack_data} não encontrado.")
    print("Execute a etapa de EDA (main.py) primeiro para gerar este arquivo.")
    exit()

print(f"Dados do Knapsack carregados: {len(df_knapsack)} estações (itens).")

# --- 2. e 3. MODELAGEM E IMPLEMENTAÇÃO ---
print("\n--- 3. IMPLEMENTAÇÃO DO BRANCH AND BOUND ---")

# Definição do Orçamento (Capacidade W)
# Definir um orçamento hipotético, ex: 20% do "custo" (Peso) total
total_weight_available = df_knapsack['Peso'].sum()
W_CAPACITY = total_weight_available * 0.20 

# Executa o solver
solve_knapsack_bb(df_knapsack, W_CAPACITY)

print("\n--- Execução Completa Finalizada ---")