import pandas as pd
import pytest

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.solver_bb_updated import calculate_bound, solve_knapsack_bb_updated, Item

def test_calculate_bound_basic():
    items = [Item('A', 60, 10, 6), Item('B', 100, 20, 5)]
    bound = calculate_bound(items, 50, 2, 0, 0, 0)
    assert bound == 160

def test_knapsack_optimal_small():
    data = {'Station': ['A', 'B', 'C'], 'Valor': [60, 100, 120], 'Peso': [10, 20, 30]}
    df = pd.DataFrame(data)
    res = solve_knapsack_bb_updated(df, 50, 10, 100000)
    assert abs(res['max_value'] - 220) < 1e-6

def test_knapsack_empty():
    df = pd.DataFrame({'Station': [], 'Valor': [], 'Peso': []})
    res = solve_knapsack_bb_updated(df, 100, 5, 100)
    assert res['status'] == "Sem itens viáveis"

def test_bound_fractional_behavior():
    items = [Item('A', 10, 2, 5), Item('B', 10, 3, 3.3)]
    b = calculate_bound(items, 4, 2, 0, 0, 0)
    assert b > 10
