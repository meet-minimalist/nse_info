##
# @author Meet Patel <>
# @file Description
# @desc Created on 2024-07-27 11:44:36 pm
# @copyright MIT License
#

from typing import Dict, Tuple

import requests

from .nse_stock import Stock


class NseFetch:
    """
    Class to fetch stock related information from NSE website.
    """

    def __init__(self):
        """
        Constructor of NseFetch. Initializes the request session.

        Raises:
            RuntimeError: If NSE website is not responding.
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
        self.session = requests.Session()
        response = self.session.get("http://nseindia.com", headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError("NSE website is not responding.")

    def is_eq(self, comp_info: Dict) -> bool:
        """
        Given comp_info belongs to equity class or not.

        Args:
            comp_info (Dict): Company Info dict obtained from NSE website.

        Returns:
            bool: True if the comp_info belongs to equity class else False.
        """
        # Meaning of these symbols:
        # https://support.geojit.com/support/solutions/articles/89000007375-what-do-the-eq-be-bl-bt-il-etc-series-stand-for-on-nse-#:~:text=Equity,intraday%20trading%20is%20not%20allowed.
        if comp_info["activeSeries"][0] in ["EQ", "BE"]:
            return True
        # For SME equities: https://www.nseindia.com/products-services/emerge-sme-market-segment
        # if ("SM" in comp_info['activeSeries']) or ("ST" in comp_info['activeSeries']) or ("SO" in comp_info['activeSeries']):
        #     return True
        return False

    def get_stock_info(self, symbol: str) -> Tuple[bool, Stock]:
        """
        Get the stock information of a given symbol from NSE website.

        Args:
            symbol (str): Stock symbol.

        Raises:
            RuntimeError: In case of failure to fetch stock info for given
                symbol from NSE website.

        Returns:
            Tuple[bool, Stock]: Tuple of 2 value.
                - First value represents the status of the operation.
                - Second value represents the Stock information.
        """
        url1 = (
            "https://www.nseindia.com/api/quote-equity?symbol="
            + symbol.replace(" ", "%20").replace("&", "%26")
            + "&section=trade_info"
        )
        url2 = "https://www.nseindia.com/api/quote-equity?symbol=" + symbol.replace(
            " ", "%20"
        ).replace("&", "%26")
        data_1 = self.session.get(url1, headers=self.headers).json()
        data_2 = self.session.get(url2, headers=self.headers).json()

        if data_1.get("marketDeptOrderBook", None) is None:
            raise RuntimeError(
                f"Unable to fetch stock info for Given symbol: {symbol}."
            )
        if data_2.get("info", None) is None:
            raise RuntimeError(
                f"Unable to fetch stock info for Given symbol: {symbol}."
            )
        total_market_cap_in_cr = data_1["marketDeptOrderBook"]["tradeInfo"][
            "totalMarketCap"
        ]
        comp_name = data_2["info"]["companyName"]

        is_eq = self.is_eq(data_2["info"])
        if not is_eq:
            return False, None

        is_suspended = data_2["info"]["isSuspended"]
        is_delisted = data_2["info"]["isDelisted"]
        is_fno = data_2["info"]["isFNOSec"]
        meta_data_industry = data_2["metadata"]["industry"]
        listing_date = data_2["metadata"]["listingDate"]
        adjusted_pe = data_2["metadata"]["pdSectorPe"]
        comp_pe = data_2["metadata"]["pdSymbolPe"]
        comp_index = data_2["metadata"]["pdSectorInd"]
        if comp_index is not None:
            comp_index = comp_index.strip()
        surv_info_cat = data_2["securityInfo"]["surveillance"]["surv"]
        surv_info_desc = data_2["securityInfo"]["surveillance"]["desc"]
        face_value = data_2["securityInfo"]["faceValue"]
        total_shares = data_2["securityInfo"]["issuedSize"]
        industry_info_macro = data_2["industryInfo"]["macro"]
        industry_info_sector = data_2["industryInfo"]["sector"]
        industry_info_ind = data_2["industryInfo"]["industry"]
        industry_info_basic_ind = data_2["industryInfo"]["basicIndustry"]

        stock_data = {
            "comp_symbol": symbol,
            "total_market_cap_in_cr": total_market_cap_in_cr,
            "comp_name": comp_name,
            "is_equity": is_eq,
            "is_suspended": is_suspended,
            "is_delisted": is_delisted,
            "is_fno": is_fno,
            "meta_data_industry": meta_data_industry,
            "listing_date": listing_date,
            "adjusted_pe": adjusted_pe,
            "comp_pe": comp_pe,
            "comp_index": comp_index,
            "surv_info_cat": surv_info_cat,
            "surv_info_desc": surv_info_desc,
            "face_value": face_value,
            "total_shares": total_shares,
            "industry_info_macro": industry_info_macro,
            "industry_info_sector": industry_info_sector,
            "industry_info_ind": industry_info_ind,
            "industry_info_basic_ind": industry_info_basic_ind,
        }
        return True, Stock(**stock_data)
