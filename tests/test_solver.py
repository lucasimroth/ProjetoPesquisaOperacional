import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.solver_bb_updated import Item, calculate_bound, solve_knapsack_bb_updated


def test_calculate_bound_basic():
    items = [Item("A", 60, 10, 6), Item("B", 100, 20, 5)]
    bound = calculate_bound(items, 50, len(items), 0, 0, 0)
    assert bound == 160


def test_calculate_bound_returns_zero_when_overweight():
    items = [Item("A", 60, 10, 6)]
    bound = calculate_bound(items, 5, len(items), 0, 6, 60)
    assert bound == 0


@pytest.mark.parametrize(
    "level,current_weight,current_value,expected_bound",
    [
        (0, 0, 0, 16.666666666666668),  # inclui frações após considerar todos os itens
        (1, 2, 10, 16.666666666666668),  # já tem primeiro item e continua fracionando
    ],
)
def test_bound_fractional_behavior(level, current_weight, current_value, expected_bound):
    items = [
        Item("A", 10, 2, 5),
        Item("B", 10, 3, 10 / 3),
        Item("C", 5, 6, 5 / 6),
    ]
    bound = calculate_bound(items, 4, len(items), level, current_weight, current_value)
    assert pytest.approx(bound) == expected_bound


def test_knapsack_optimal_small():
    data = {
        "Station": ["A", "B", "C"],
        "Valor": [60, 100, 120],
        "Peso": [10, 20, 30],
    }
    df = pd.DataFrame(data)
    res = solve_knapsack_bb_updated(df, 50, time_limit=10, max_nodes_limit=100_000)
    assert abs(res["max_value"] - 220) < 1e-6
    assert res["status"] == "Ótimo Encontrado"
    assert res["solutions_found"] >= 1


def test_knapsack_empty():
    df = pd.DataFrame({"Station": [], "Valor": [], "Peso": []})
    res = solve_knapsack_bb_updated(df, 100, time_limit=5, max_nodes_limit=100)
    assert res["status"] == "Sem itens viáveis"
    assert res["max_value"] == 0
    assert res["nodes_expanded"] == 0


def test_state_generation_produces_valid_solution_and_depth():
    df = pd.DataFrame(
        {
            "Station": ["A", "B", "C"],
            "Valor": [40, 50, 100],
            "Peso": [4, 5, 10],
        }
    )
    capacity = 14
    res = solve_knapsack_bb_updated(df, capacity, time_limit=5, max_nodes_limit=1000)
    assert res["status"] == "Ótimo Encontrado"
    assert res["final_weight"] <= capacity
    expected_items = {"A", "C"}
    assert set(res["final_solution_items"]) == expected_items
    assert res["max_depth_reached"] >= res["total_items_viable"] - 1
    assert res["solutions_found"] >= 1


def test_branch_and_bound_pruning_counters():
    df = pd.DataFrame(
        {
            "Station": ["A", "B", "C"],
            "Valor": [10, 9, 5],
            "Peso": [5, 4, 3],
        }
    )
    res = solve_knapsack_bb_updated(df, 7, time_limit=5, max_nodes_limit=1000)
    assert res["status"] == "Ótimo Encontrado"
    assert res["pruned_by_viability"] > 0
    assert res["pruned_by_bound"] > 0
    assert res["max_value"] == 14
