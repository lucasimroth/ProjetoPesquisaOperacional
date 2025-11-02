# Otimização de Portfólio de Estações com Branch and Bound

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-blueviolet?style=for-the-badge&logo=pandas)
![NumPy](https://img.shields.io/badge/NumPy-white?style=for-the-badge&logo=numpy)
![Licença](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

Este é um projeto acadêmico para a disciplina de Pesquisa Operacional que aplica o algoritmo **Branch and Bound (B&B)** a um problema de seleção de portfólio.

Utilizando dados de fluxo de passageiros do sistema de transporte público, o objetivo é determinar o conjunto ótimo de estações para um "projeto de melhoria" (modernização, publicidade, etc.). O projeto é modelado como um **Problema da Mochila 0-1 (Knapsack Problem)**, onde buscamos maximizar o "Valor" (fluxo anual de passageiros) sem exceder um "Peso" (orçamento de custo, representado pelo fluxo semanal).

## 🧮 Modelagem do Problema (Definição Formal)

O problema foi mapeado como um **Problema da Mochila 0-1 (Knapsack Problem)**:

* **Itens:** $n$ estações de transporte.
* **Variáveis de Decisão:** $x_i \in \{0, 1\}$ para cada estação $i$, onde $x_i = 1$ se a estação for selecionada e $x_i = 0$ caso contrário.

#### Função Objetivo (Maximização)

Maximizar o retorno total (soma do fluxo anual em milhões de passageiros) das estações selecionadas.

$$
\text{Maximizar } Z = \sum_{i=1}^{n} v_i x_i
$$

#### Restrições

1.  **Orçamentária (Peso):** O custo (peso) total das estações selecionadas não pode exceder a capacidade máxima $W$.
    $$
    \sum_{i=1}^{n} w_i x_i \leq W
    $$

2.  **Integridade:** A decisão para cada estação é binária.
    $$
    x_i \in \{0, 1\}, \quad \forall i = 1, \ldots, n
    $$

#### Parâmetros do Modelo:
* $v_i$: Valor da estação $i$ (extraído da coluna `AnnualEntryExit_Mill`).
* $w_i$: Peso (custo) da estação $i$ (extraído da coluna `Entry_Week`).
* $W$: Orçamento total (Capacidade da mochila), definido em `main.py` como uma porcentagem do peso total.

---

### 🛠️ Construído Com

* [Python](https://www.python.org/)
* [Pandas](https://pandas.pydata.org/)
* [NumPy](https://numpy.org/)
* [Matplotlib](https://matplotlib.org/)
* [Seaborn](https://seaborn.pydata.org/)

---

## 🚀 Começando

Instruções sobre como configurar e executar o projeto localmente.

### Pré-requisitos

O que os usuários precisam ter instalado antes de começar?

* Python 3.9+
* pip
    ```sh
    python -m ensurepip --upgrade
    ```

### 📦 Instalação

Um guia passo a passo sobre como colocar o ambiente de desenvolvimento para rodar.

1.  Clone o repositório
    ```sh
    git clone [https://github.com/seu_usuario/nome_do_projeto.git](https://github.com/seu_usuario/nome_do_projeto.git)
    ```
2.  Navegue até a pasta do projeto
    ```sh
    cd nome_do_projeto
    ```
3.  (Recomendado) Crie um ambiente virtual
    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
4.  Instale as dependências
    ```sh
    pip install -r requirements.txt
    ```

---

## Estrutura do projeto:

Claro, aqui está a estrutura de pastas e arquivos para copiar e colar:

```
.
├── data
│   ├── raw
│   └── processed
├── reports
│   └── figures
├── src
│   ├── data_processing.py
│   └── solver_bb.py
├── main.py
├── requirements.txt
└── README.md
```

## 🏃 Uso

Para executar o fluxo completo (carga, limpeza, EDA e otimização B&B), execute o script principal:

```sh
python main.py
