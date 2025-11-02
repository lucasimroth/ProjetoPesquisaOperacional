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
            break # Este 'break' é crucial
            
    return bound

def solve_knapsack_bb(df_knapsack, W_CAPACITY):
    """
    Resolve o Problema da Mochila 0-1 usando Branch and Bound com Busca em Profundidade (Pilha).
    """
    
    print("Iniciando Solver Branch and Bound...")
    print(f"Capacidade (W): {W_CAPACITY:.2f}")
    
    # --- 1. Preparação dos Itens ---
    items = []
    for _, row in df_knapsack.iterrows():
        # Ignora itens que sozinhos já estouram o peso (poda inicial)
        if row['Peso'] <= W_CAPACITY and row['Peso'] > 0:
            ratio = row['Valor'] / row['Peso']
            items.append(Item(row['Station'], row['Valor'], row['Peso'], ratio))

    # Ordena por 'ratio' (valor/peso) decrescente. Essencial para o cálculo do bound.
    items.sort(key=lambda x: x.ratio, reverse=True)
    n = len(items)
    print(f"Itens viáveis (estações): {n}")

    # --- 2. Inicialização do B&B ---
    stack = []  # Pilha de estados (DFS)
    
    # Nó inicial: (level, weight, value, path_list)
    # level: índice do item a ser decidido
    # path_list: lista de 0s e 1s representando as decisões
    initial_node = (0, 0, 0, []) 
    stack.append(initial_node)
    
    max_value = 0.0  # Melhor valor encontrado (Lower Bound, Z_underline)
    best_solution_path = []

    # --- 3. Métricas de Execução (Seção 3.2) ---
    nodes_expanded = 0
    max_depth_reached = 0
    solutions_found = 0
    start_time = time.time()

    # --- 4. Loop Principal (DFS) ---
    while stack:
        level, current_weight, current_value, current_path = stack.pop()
        
        nodes_expanded += 1
        max_depth_reached = max(max_depth_reached, level)

        # --- Caso Base: Fim da árvore (folha) ---
        if level == n:
            if current_value > max_value:
                max_value = current_value
                best_solution_path = current_path
                solutions_found += 1
            continue # Fim do ramo

        item = items[level]

        # --- Ramo 1: INCLUIR o item 'level' (Nó da Esquerda) ---
        weight_incl = current_weight + item.weight
        value_incl = current_value + item.value
        path_incl = current_path + [1]

        # Poda por Viabilidade (Peso): Só explora se couber na mochila
        if weight_incl <= W_CAPACITY:
            # Atualiza o melhor valor se esta for uma solução (parcial) melhor
            if value_incl > max_value:
                max_value = value_incl
                best_solution_path = path_incl
                solutions_found += 1
            
            # Poda por Limite (Bound): Calcula o bound e verifica se vale a pena
            bound_incl = calculate_bound(items, W_CAPACITY, n, level + 1, weight_incl, value_incl)
            
            if bound_incl > max_value:
                stack.append((level + 1, weight_incl, value_incl, path_incl))

        # --- Ramo 2: NÃO INCLUIR o item 'level' (Nó da Direita) ---
        weight_excl = current_weight
        value_excl = current_value
        path_excl = current_path + [0]
        
        # Poda por Limite (Bound): Verifica se este ramo pode superar o max_value
        bound_excl = calculate_bound(items, W_CAPACITY, n, level + 1, weight_excl, value_excl)
        
        if bound_excl > max_value:
            stack.append((level + 1, weight_excl, value_excl, path_excl))

    # --- 5. Finalização e Relatório de Métricas ---
    end_time = time.time()
    exec_time = end_time - start_time
    
    # Formata a solução final
    final_solution_items = []
    final_weight = 0.0
    for i, taken in enumerate(best_solution_path):
        if i < len(items) and taken == 1: # Garante que o path corresponda aos itens
            final_solution_items.append(items[i].name)
            final_weight += items[i].weight
    
    print("-" * 50)
    print("--- Solver B&B Concluído ---")
    print(f"Valor Máximo (Retorno): {max_value:.4f} (milhões anuais)")
    print(f"Peso Total (Custo): {final_weight:.2f} (de {W_CAPACITY:.2f} disponíveis)")
    print(f"Estações Selecionadas: {len(final_solution_items)}")
    # print(final_solution_items) # Descomente para ver a lista

    print("\n--- Métricas de Execução (3.2) ---")
    print(f"Tempo Total de Execução: {exec_time:.6f} segundos")
    print(f"Número de Nós Expandidos: {nodes_expanded}")
    print(f"Profundidade Máxima Atingida: {max_depth_reached}")
    print(f"Soluções Viáveis Encontradas: {solutions_found}")
    print("-" * 50)

    return max_value, final_solution_items, final_weight