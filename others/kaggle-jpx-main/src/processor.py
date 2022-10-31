import numpy as np
import pandas as pd
from typing import Dict


class ScoringService:
    dfs: Dict[str, pd.DataFrame] = {}
    codes: list = []
    dataset_base_labels = ['prices', 'stock_list', 'options_spec', 'stock_fin_spec', 'stock_list_spec', 'stock_price_spec', 'trades_spec']

    @classmethod
    def get_input_dirs(cls) -> dict:
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

    @classmethod
    def get_dataset_with_input_dirs(cls, input_dirs: dict, debug=False) -> Dict[str, pd.DataFrame]:
        if cls.dfs is None:
            cls.dfs = {}
        for key, value in input_dirs.items():
            if debug:
                if key in cls.dataset_base_labels:
                    cls.dfs[key] = pd.read_csv(value)
                else:
                    continue
            else:
                cls.dfs[key] = pd.read_csv(value)
        return cls.dfs

    @classmethod
    def get_dataset(cls, debug=False) -> Dict[str, pd.DataFrame]:
        input_dirs = cls.get_input_dirs()
        return cls.get_dataset_with_input_dirs(input_dirs, debug)

    @classmethod
    def merge_main_and_sup_file(cls):
        for label in cls.dataset_base_labels:
            label_main = label + '_main'
            label_sup = label + '_sup'
            df_merged = pd.concat([cls.dfs[label_main], cls.dfs[label_sup]])
            cls.dfs[label] = df_merged

    @classmethod
    def get_technical(cls, dfs: Dict[str, pd.DataFrame], code: int):
        tmp_df = dfs["prices"][dfs["prices"]["SecuritiesCode"] == code].copy()

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

    @classmethod
    def get_codes(cls, dfs: Dict[str, pd.DataFrame]) -> list:
        stock_list = dfs["stock_list"].copy()
        cls.codes = stock_list[stock_list["Universe0"]]["SecuritiesCode"].values
        return cls.codes

    @classmethod
    def get_df_merge_with_dfs(cls, dfs, debug=False):
        cls.merge_main_and_sup_file()
        df_technical = []
        codes = cls.get_codes(cls.dfs)
        if debug:
            codes = codes[0:2]
        for code in codes:
            df_technical.append(cls.get_technical(dfs, code))
        df_technical = pd.concat(df_technical)
        df_merge = df_technical
        return df_merge

    @classmethod
    def get_df_merge(cls, debug=False):
        if not bool(cls.dfs):
            cls.get_dataset(debug)
        return cls.get_df_merge_with_dfs(cls.dfs, debug)
