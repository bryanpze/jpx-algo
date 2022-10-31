import numpy as np
import pandas as pd
from typing import Dict, List


class DataFrames:
    def __init__(self):
        self.dfs: Dict[str, pd.DataFrame] = {}

    def __getitem__(self, key: str):
        return self.dfs[key]

    def __setitem__(self, key: str, df: pd.DataFrame):
        self.dfs[key] = df

    def is_empty(self) -> bool:
        return not bool(self.dfs)

    def keys(self):
        return self.dfs.keys()


class DataLoader:
    @staticmethod
    def get_input_dirs() -> dict:
        root_dir = '/Users/mogitaketo/code/kaggle/jpx'
        root_input_dir = root_dir + '/input/jpx-tokyo-stock-exchange-prediction/'
        input_dirs: dict = {}
        train_files_filenames = {
            'prices': 'stock_prices.csv',
            'prices_sec': 'secondary_stock_prices.csv',
            'fins': 'financials.csv',
            'options': 'options.csv',
            'trades': 'trades.csv'
        }
        for key, value in train_files_filenames.items():
            input_dirs[key + '_main'] = root_input_dir + 'train_files/' + value
        for key, value in train_files_filenames.items():
            input_dirs[key + '_sup'] = root_input_dir + 'supplemental_files/' + value
        input_dirs['stock_list'] = root_input_dir + "stock_list.csv"
        data_spec_filenames = ['options_spec', 'stock_fin_spec', 'stock_list_spec', 'stock_price_spec', 'trades_spec']
        for key in data_spec_filenames:
            input_dirs[key] = root_input_dir + 'data_specifications/' + key + '.csv'
        return input_dirs

    @staticmethod
    def get_dataset(debug=False) -> DataFrames:
        dfs = DataFrames()
        input_dirs = DataLoader.get_input_dirs()
        debug_get_dataset_list = [
            'prices_main', 'prices_sup', 'stock_list', 'options_spec',
            'stock_fin_spec', 'stock_list_spec', 'stock_price_spec', 'trades_spec'
        ]
        for key, value in input_dirs.items():
            if debug and key not in debug_get_dataset_list:
                continue
            dfs[key] = pd.read_csv(value)
        return dfs


class Preprocessor:
    @staticmethod
    def merge_main_and_sup_file(dfs: DataFrames, debug=False) -> DataFrames:
        for label in ['prices', 'prices_sec', 'fins', 'options', 'trades']:
            label_main = label + '_main'
            label_sup = label + '_sup'
            if debug and label_main not in dfs.keys():
                continue
            df_merged = pd.concat([dfs[label_main], dfs[label_sup]])
            dfs[label] = df_merged
        return dfs

    @staticmethod
    def preprocessing(dfs: DataFrames, debug=False) -> DataFrames:
        dfs = Preprocessor.merge_main_and_sup_file(dfs, debug)
        return dfs


class ScoringService:
    dfs: DataFrames
    codes: List[int]

    def __init__(self):
        self.dfs = DataFrames()

    """
    def get_dataset(self, debug=False) -> None:
        self.dfs = DataLoader.get_dataset(debug)
    """
    def get_technical(self, dfs: DataFrames, code: int, debug=False):
        tmp_df = dfs["prices"][dfs["prices"]["SecuritiesCode"] == code].copy()
        if False and debug:
            tmp_df = tmp_df.iloc[-5:, :].copy()
        # 前日終値
        tmp_df['PreviousClose'] = tmp_df['Close'].shift()

        # 騰落率 percentage change
        tmp_df["pct_change_1"] = tmp_df["Close"].pct_change(1)
        tmp_df["pct_change_5"] = tmp_df["Close"].pct_change(5)
        tmp_df["pct_change_10"] = tmp_df["Close"].pct_change(10)
        tmp_df["pct_change_20"] = tmp_df["Close"].pct_change(20)
        tmp_df["pct_change_40"] = tmp_df["Close"].pct_change(40)
        tmp_df["pct_change_60"] = tmp_df["Close"].pct_change(60)
        tmp_df["pct_change_100"] = tmp_df["Close"].pct_change(100)

        # 売買代金（traded value?） （出来高はvolume）
        tmp_df["val"] = tmp_df["Close"] * tmp_df["Volume"]
        tmp_df = tmp_df.replace([np.inf, -np.inf], np.nan)
        tmp_df["val_1"] = tmp_df["Volume"]
        tmp_df["val_5"] = tmp_df["Volume"].rolling(5).mean()
        tmp_df["val_10"] = tmp_df["Volume"].rolling(10).mean()
        tmp_df["val_20"] = tmp_df["Volume"].rolling(20).mean()
        tmp_df["val_40"] = tmp_df["Volume"].rolling(40).mean()
        tmp_df["val_60"] = tmp_df["Volume"].rolling(60).mean()
        tmp_df["val_100"] = tmp_df["Volume"].rolling(100).mean()
        tmp_df["d_vol"] = tmp_df["Volume"]/tmp_df["val_20"]  # dとは？

        # レンジ range  ATR: Average True Range
        tmp_df["range"] = (tmp_df[["PreviousClose", "High"]].max(axis=1) - tmp_df[["PreviousClose", "Low"]].min(axis=1)) / tmp_df["PreviousClose"]
        tmp_df = tmp_df.replace([np.inf, -np.inf], np.nan)
        tmp_df["atr_1"] = tmp_df["range"]
        tmp_df["atr_5"] = tmp_df["range"].rolling(5).mean()
        tmp_df["atr_10"] = tmp_df["range"].rolling(10).mean()
        tmp_df["atr_20"] = tmp_df["range"].rolling(20).mean()
        tmp_df["atr_40"] = tmp_df["range"].rolling(40).mean()
        tmp_df["atr_60"] = tmp_df["range"].rolling(60).mean()
        tmp_df["atr_100"] = tmp_df["range"].rolling(100).mean()
        tmp_df["d_atr"] = tmp_df["range"]/tmp_df["atr_20"]
        return tmp_df

    def get_codes(self, dfs: DataFrames) -> list:
        stock_list = dfs["stock_list"].copy()
        self.codes = stock_list[stock_list["Universe0"]]["SecuritiesCode"].values
        return self.codes

    def get_df_merge(self, debug=False):
        if self.dfs.is_empty():
            self.dfs = DataLoader.get_dataset(debug)
        self.dfs = Preprocessor.preprocessing(self.dfs, debug)
        df_technical = []
        codes = self.get_codes(self.dfs)
        if debug:
            codes = codes[0:2]
        for code in codes:
            df_technical.append(self.get_technical(self.dfs, code, debug))
        df_technical = pd.concat(df_technical)
        df_merge = df_technical
        return df_merge


if __name__ == '__main__':
    print('test')
