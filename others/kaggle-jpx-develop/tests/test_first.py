import pandas as pd
from kaggle_jpx_package import DataFrames, DataLoader


def test_first():
    assert(1) == 1


def test_DataFrames_is_empty():
    dfs = DataFrames()
    assert dfs.is_empty()


def test_DataFrames_is_not_empty():
    dfs = DataFrames()
    dfs['test'] = pd.DataFrame([[1, 2], [3, 4]])
    assert dfs.is_empty() is False


def test_DataFrames_keys():
    dfs = DataFrames()
    dfs['test'] = pd.DataFrame([[1, 2], [3, 4]])
    dfs['test2'] = pd.DataFrame([[1, 2], [3, 4]])
    keys = list(dfs.keys())
    assert keys == ['test', 'test2']


def test_DataLoader_get_dataset_debug():
    dfs = DataLoader().get_dataset(debug=True)
    dfs_keys_list = list(dfs.keys())
    assert dfs_keys_list == [
            'prices_main', 'prices_sup', 'stock_list', 'options_spec',
            'stock_fin_spec', 'stock_list_spec', 'stock_price_spec', 'trades_spec'
        ]
