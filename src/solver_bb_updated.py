import time
from collections import namedtuple

# Namedtuple para facilitar a leitura do código
Item = namedtuple('Item', ['name', 'value', 'weight', 'ratio'])


def calculate_bound(items, W, n, level, current_weight, current_value):
    """
    Calcula o Limite Superior (Bound) usando a relaxação linear (método guloso).
    Assume que os 'items' já estão ordenados por ratio (valor/peso).
    """
    if current_weight > W:
        return 0  # Inviável

    bound = current_value
    total_weight = current_weight

    # Itera a partir do item 'level'
    for i in range(level, n):
        # Se o item cabe inteiramente
        if total_weight + items[i].weight <= W:
            total_weight += items[i].weight
            bound += items[i].value
        else:
            # Se não cabe, pega a fração (relaxação) e para
            remaining_capacity = W - total_weight
            bound += items[i].ratio * remaining_capacity
            break  # Este 'break' é crucial

    return bound


def solve_knapsack_bb_updated(df_knapsack, W_CAPACITY,
                              time_limit=60,
                              max_nodes_limit=1_000_000_000,
                              st_progress_placeholders=None):
    """
    Resolve o Problema da Mochila 0-1 usando Branch and Bound com Busca em Profundidade (Pilha).

    Modificado para aceitar limites e reportar progresso via placeholders do Streamlit.
    """

    # --- 1. Preparação dos Itens ---
    items = []
    for _, row in df_knapsack.iterrows():
        if row['Peso'] <= W_CAPACITY and row['Peso'] > 0:
            ratio = row['Valor'] / row['Peso']
            items.append(Item(row['Station'], row['Valor'], row['Peso'], ratio))

    items.sort(key=lambda x: x.ratio, reverse=True)
    n = len(items)

    if n == 0:
        return {
            "max_value": 0.0, "final_solution_items": [], "final_weight": 0.0,
            "exec_time": 0.0, "nodes_expanded": 0, "max_depth_reached": 0,
            "solutions_found": 0, "pruned_by_viability": 0, "pruned_by_bound": 0,
            "status": "Sem itens viáveis"
        }

    # --- 2. Inicialização do B&B ---
    stack = [(0, 0, 0, [])]  # (level, weight, value, path_list)
    max_value = 0.0  # Lower Bound (Z_underline)
    best_solution_path = []

    # --- 3. Métricas de Execução (Seção 3.2 e 4.3) ---
    nodes_expanded = 0
    max_depth_reached = 0
    solutions_found = 0
    pruned_by_viability = 0
    pruned_by_bound = 0
    start_time = time.time()
    status = "Em execução"

    # Frequência de atualização do dashboard (a cada N nós)
    UPDATE_FREQ = 1000

    # --- 4. Loop Principal (DFS) ---
    while stack:
        level, current_weight, current_value, current_path = stack.pop()

        nodes_expanded += 1
        max_depth_reached = max(max_depth_reached, level)

        # --- Verificação de Limites (4.3) ---
        if nodes_expanded > max_nodes_limit:
            status = "Limite de Nós Atingido"
            break

        exec_time = time.time() - start_time
        if exec_time > time_limit:
            status = "Limite de Tempo Atingido"
            break

        # --- Atualização de Progresso (4.3) ---
        if st_progress_placeholders and nodes_expanded % UPDATE_FREQ == 0:
            st_progress_placeholders["nodes"].metric(
                "Nós Expandidos", f"{nodes_expanded:,}")
            st_progress_placeholders["pruning"].metric(
                "Podas (Bound/Viab.)", f"{pruned_by_bound:,} / {pruned_by_viability:,}")
            st_progress_placeholders["time"].metric(
                "Tempo Decorrido (s)", f"{exec_time:.2f}")

        # --- Caso Base: Fim da árvore (folha) ---
        if level == n:
            if current_value > max_value:
                max_value = current_value
                best_solution_path = current_path
                solutions_found += 1
                # Atualiza o melhor valor em tempo real
                if st_progress_placeholders:
                    st_progress_placeholders["lower_bound"].metric(
                        "Melhor Valor (Z)", f"{max_value:.4f}")
            continue

        item = items[level]

        # --- Ramo 1: INCLUIR o item 'level' (Nó da Esquerda) ---
        weight_incl = current_weight + item.weight
        value_incl = current_value + item.value
        path_incl = current_path + [1]

        if weight_incl <= W_CAPACITY:
            if value_incl > max_value:
                max_value = value_incl
                best_solution_path = path_incl
                solutions_found += 1
                # Atualiza o melhor valor em tempo real
                if st_progress_placeholders:
                    st_progress_placeholders["lower_bound"].metric(
                        "Melhor Valor (Z)", f"{max_value:.4f}")

            bound_incl = calculate_bound(items, W_CAPACITY, n, level + 1, weight_incl, value_incl)

            if bound_incl > max_value:
                stack.append((level + 1, weight_incl, value_incl, path_incl))
            else:
                pruned_by_bound += 1  # Poda por Limite
        else:
            pruned_by_viability += 1  # Poda por Viabilidade

        # --- Ramo 2: NÃO INCLUIR o item 'level' (Nó da Direita) ---
        weight_excl = current_weight
        value_excl = current_value
        path_excl = current_path + [0]

        bound_excl = calculate_bound(items, W_CAPACITY, n, level + 1, weight_excl, value_excl)

        if bound_excl > max_value:
            stack.append((level + 1, weight_excl, value_excl, path_excl))
        else:
            pruned_by_bound += 1  # Poda por Limite

    # --- 5. Finalização e Retorno ---
    if status == "Em execução":
        status = "Ótimo Encontrado"

    end_time = time.time()
    exec_time = end_time - start_time

    # Formata a solução final
    final_solution_items = []
    final_weight = 0.0
    for i, taken in enumerate(best_solution_path):
        if i < len(items) and taken == 1:
            final_solution_items.append(items[i].name)
            final_weight += items[i].weight

    # Retorna um dicionário com todas as métricas
    return {
        "max_value": max_value,
        "final_solution_items": final_solution_items,
        "final_weight": final_weight,
        "exec_time": exec_time,
        "nodes_expanded": nodes_expanded,
        "max_depth_reached": max_depth_reached,
        "solutions_found": solutions_found,
        "pruned_by_viability": pruned_by_viability,
        "pruned_by_bound": pruned_by_bound,
        "status": status,
        "W_CAPACITY": W_CAPACITY,
        "total_items_viable": n,
        "time_limit": time_limit,
        "max_nodes_limit": max_nodes_limit
    }