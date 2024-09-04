"""
 # @ Author: Meet Patel
 # @ Create Time: 2024-07-30 19:53:29
 # @ Modified by: Meet Patel
 # @ Modified time: 2024-07-30 19:58:20
 # @ Description:
 """

import json

import pandas as pd
from pandas import DataFrame


class Stock:
    def __init__(self, **kwargs):
        """
        Class representing stock information obtained from NSE website.
        """
        self.stock_info = kwargs
        self.comp_symbol = kwargs.get("comp_symbol", None)
        self.comp_name = kwargs.get("comp_name", None)
        self.is_suspended = kwargs.get("is_suspended", None)
        self.is_delisted = kwargs.get("is_delisted", None)
        self.is_fno = kwargs.get("is_fno", None)
        self.meta_data_industry = kwargs.get("meta_data_industry", None)
        self.listing_date = kwargs.get("listing_date", None)
        self.adjusted_pe = kwargs.get("adjusted_pe", None)
        self.comp_pe = kwargs.get("comp_pe", None)
        self.comp_index = kwargs.get("comp_index", None)
        self.surv_info_cat = kwargs.get("surv_info_cat", None)
        self.surv_info_desc = kwargs.get("surv_info_desc", None)
        self.face_value = kwargs.get("face_value", None)
        self.total_shares = kwargs.get("total_shares", None)
        self.industry_info_macro = kwargs.get("industry_info_macro", None)
        self.industry_info_sector = kwargs.get("industry_info_sector", None)
        self.industry_info_ind = kwargs.get("industry_info_ind", None)
        self.industry_info_basic_ind = kwargs.get("industry_info_basic_ind", None)

    def to_json_string(self) -> str:
        """
        Get the json string representation of the stock data.

        Returns:
            str: String representation of stock.
        """
        json_string = json.dumps(self.stock_info)
        return json_string

    def to_dataframe(self) -> DataFrame:
        """
        Get the pandas dataframe representation of stock data.

        Returns:
            DataFrame: Pandas dataframe representation of stock.
        """
        return pd.DataFrame([self.stock_info])
