# Documentação de Testes Automatizados

## Visão Geral
- Escopo: funções críticas do `solver_bb_updated`, cobrindo cálculo de bound, geração/validação de estados e podas com verificação da solução ótima.
- Ferramenta: `pytest` 9.0.0 em Python 3.13.3 (Windows 10).
- Localização dos testes: `tests/test_solver.py`.

## Cenários de Teste
- `test_calculate_bound_basic` e `test_calculate_bound_returns_zero_when_overweight`: validam o cálculo do bound em condições normais e quando o estado excede a capacidade.
- `test_bound_fractional_behavior`: confirma o uso da relaxação fracionária no cálculo do bound em diferentes níveis da árvore.
- `test_knapsack_optimal_small` e `test_state_generation_produces_valid_solution_and_depth`: asseguram que a geração de estados mantém viabilidade, encontra a combinação ótima e registra métricas coerentes (peso final, profundidade e soluções encontradas).
- `test_knapsack_empty`: verifica o tratamento de instâncias sem itens viáveis.
- `test_branch_and_bound_pruning_counters`: garante que as contagens de poda por viabilidade e por bound são incrementadas quando apropriado e que o valor ótimo é preservado.

## Execução
- Comando: `pytest`
- Resultado: `8 passed in 0.57s`
- Evidência: execução registrada após as alterações deste conjunto de testes.
