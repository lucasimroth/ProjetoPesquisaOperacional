import pandas as pd
import os

def carregar_e_limpar_dados(pasta_raw, pasta_processed, nome_arquivo="dados_limpos.csv"):
    """
    Lê todos os CSVs da pasta raw, adiciona coluna Ano, concatena,
    remove duplicatas e salva em processed.
    Retorna o DataFrame limpo.
    """
    arquivos_csv = [f for f in os.listdir(pasta_raw) if f.endswith('.csv')]
    dataframes = []

    for arquivo in arquivos_csv:
        caminho = os.path.join(pasta_raw, arquivo)
        ano = int(arquivo.split('_')[0])
        df = pd.read_csv(caminho)
        df['Ano'] = ano
        dataframes.append(df)

    # Concatena todos os DataFrames
    dados = pd.concat(dataframes, ignore_index=True)

    # Remove duplicatas
    dados = dados.drop_duplicates()

    # Salva o CSV limpo na pasta processed
    os.makedirs(pasta_processed, exist_ok=True)
    caminho_saida = os.path.join(pasta_processed, nome_arquivo)
    dados.to_csv(caminho_saida, index=False)
    print(f"Dados limpos salvos em: {caminho_saida}")

    return dados
