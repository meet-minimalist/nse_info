##
# @author Meet Patel <>
# @file Description
# @desc Created on 2024-09-01 4:27:18 pm
# @copyright MIT License
#

from typing import List

import pandas as pd


def check_code_exists(comp_code: str) -> bool:
    """
    Checks whether a given company code exists in NSE stock market.

    Args:
        comp_code (str): Code of the company list in NSE

    Returns:
        bool: True if exists else False
    """
    list_of_codes = get_list_of_codes()
    return comp_code in list_of_codes


def get_list_of_codes() -> List[str]:
    """
    Get the list of all the company codes which are present in NSE stock market.

    Returns:
        List[str]: List of company codes for all listed stocks.
    """
    eq_list_pd = pd.read_csv(
        "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    )
    return eq_list_pd["SYMBOL"].tolist()
