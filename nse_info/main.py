##
# @author Meet Patel <>
# @file Description
# @desc Created on 2024-07-27 11:44:56 pm
# @copyright MIT License
#
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List

import pandas as pd

from .fetch_nse import NseFetch
from .utils.stock_code_helper import get_list_of_codes


def fetch_data_helper(nse: NseFetch, stock_codes: List[str]) -> pd.DataFrame:
    """
    Helper function to be executed inside each threads to fetch required data
    for given stock codes.

    Args:
        nse (NseFetch): NseFetch class instance
        stock_codes (List[str]): List of stock codes to fetch.

    Returns:
        pd.DataFrame: Pandas DataFrame generated from fetched data.
    """
    res = []
    for stock_code in stock_codes:
        try:
            status, stock_info = nse.get_stock_info(stock_code)
        except RuntimeError as e:
            print(
                f"No information obtained for stock: {stock_code} due to exception: {e}."
            )
            continue
        if not status:
            print(f"Stock {stock_code} is not an equity stock. Skipping the same.")
            continue
        df = stock_info.to_dataframe()
        res.append(df)
    return res


def fetch_data(num_threads: int, output_dir: str) -> None:
    """
    Fetch data of all the stocks listed on NSE.

    Args:
        num_threads (int): Number of threads to be executed for fetching.
        output_dir (str): Output directory for saving the data.
    """
    nse = NseFetch()
    all_stock_codes = get_list_of_codes()
    stocks_per_thread = len(all_stock_codes) // num_threads
    stocks_splits = []
    for thread_idx in range(num_threads):
        stock_codes_per_thread = all_stock_codes[
            thread_idx * stocks_per_thread : (thread_idx + 1) * stocks_per_thread
        ]
        stocks_splits.append(stock_codes_per_thread)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        exec = [
            executor.submit(fetch_data_helper, nse, stock_split)
            for stock_split in stocks_splits
        ]

        comb_df = []
        for e in exec:
            comb_df.extend(e.result())
        comb_df = pd.concat(comb_df)

    os.makedirs(output_dir, exist_ok=True)
    todays_date = datetime.today().strftime("%d_%m_%Y")
    csv_output_path = os.path.join(output_dir, f"all_stock_nse_data_{todays_date}.csv")
    comb_df.to_csv(csv_output_path, index=False)
    print(f"Data saved at {csv_output_path}")


def main():
    parser = argparse.ArgumentParser(description="NSE Info package help.")
    parser.add_argument(
        "-n",
        "--num_threads",
        default=10,
        type=int,
        help="Number of threads to use while fetching.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default="cached_data",
        type=str,
        help="Output directory where cached data is stored.",
    )

    args = parser.parse_args()

    fetch_data(args.num_threads, args.output_dir)


if __name__ == "__main__":
    main()
