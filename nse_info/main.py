##
# @author Meet Patel <>
# @file Description
# @desc Created on 2024-07-27 11:44:56 pm
# @copyright MIT License
#
import argparse
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from fetch_nse import NseFetch
from utils.stock_code_helper import get_list_of_codes

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def setup_logger(log_level="info") -> logging.Logger:
    """
    Setup the logger based on log level.

    Args:
        log_level (str, optional): Level of logs to be presented to console.
            Defaults to "info".

    Returns:
        logging.Logger: Logger object.
    """
    if log_level == "info":
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Format of log messages
        handlers=[logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)
    return logger


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
    logger = logging.getLogger(__name__)
    for stock_code in stock_codes:
        try:
            status, stock_info = nse.get_stock_info(stock_code)
        except RuntimeError as e:
            logger.debug(
                f"No information obtained for stock: {stock_code} due to exception: {e}."
            )
            continue
        if not status:
            logger.debug(
                f"Stock {stock_code} is not an equity stock. Skipping the same."
            )
            continue
        df = stock_info.to_dataframe()
        res.append(df)
    return res


def fetch_data(num_threads: int, output_dir: str) -> pd.DataFrame:
    """
    Fetch data of all the stocks listed on NSE.

    Args:
        num_threads (int): Number of threads to be executed for fetching.
        output_dir (str): Output directory for saving the data.

    Returns:
        pd.DataFrame: Pandas DataFrame generated from fetched data.
    """
    logger = logging.getLogger(__name__)
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

    comb_df = comb_df.sort_values(by="total_market_cap_in_cr", ascending=False)
    comb_df.to_csv(csv_output_path, index=True)
    logger.debug(f"Data saved at {csv_output_path}")

    total_stocks = len(comb_df)
    nse_total_market_cap_in_cr = comb_df["total_market_cap_in_cr"].sum()
    logger.debug(f"Total stocks in NSE: {total_stocks}")
    logger.debug(f"Total market cap in crores: {nse_total_market_cap_in_cr}")
    return comb_df


def create_pi_chart(
    data_dict: Dict, title: str = "", filename: str = "plot.png"
) -> None:
    """
    Creates a pi chart and saves the plot on the disk.

    Args:
        data_dict (Dict): Mapping of various sectors with their respective total
            market cap.
        title (str, optional): Title of pi chart. Defaults to "".
        filename (str, optional): File name where plot is to be saved.
            Defaults to "plot.png".
    """
    labels = data_dict.keys()
    sizes = data_dict.values()

    plt.figure(figsize=(8, 8))  # Size of the figure
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", shadow=False, startangle=140)

    plt.title(title)
    plt.savefig(filename, format="png")
    plt.close()


def create_sectoral_heatmap(
    sector_name: str,
    data_frame: pd.DateOffset,
    filename: str = "heatmap.png",
    top: int = 10,
) -> None:
    """
    Creates a 2D heatmap based on the provided sector information.

    Args:
        sector_name (str): Name of the sector
        data_frame (pd.DateOffset): Dataframe containins sectoral stock info.
        filename (str, optional): File name where plot is to be saved.
            Defaults to "heatmap.png".
        top (int, optional): Number of top records to be shown. Defaults to 10.
    """
    data_frame = data_frame.set_index("Company Symbol")
    data_frame = data_frame.head(top)

    plt.figure(figsize=(5, 10))
    sns.heatmap(data_frame, cmap="YlGnBu", fmt=".2f", linewidths=0.5, linecolor="black")
    plt.tight_layout()

    plt.title(f"Heat map for {sector_name}")
    plt.xlabel("Columns")
    plt.ylabel("Rows")
    plt.savefig(filename, format="png")
    plt.close()


def get_sectoral_market_cap(df: pd.DataFrame, dump_dir: str = None) -> Tuple[Dict]:
    """
    Get the sectoral information based on provided dataframe fetched from NSE
    website.

    Args:
        df (pd.DataFrame): Dataframe containing information of all the stocks.
        dump_dir (str, optional): Directory where the plots will be dumped to.
            Defaults to None.

    Returns:
        Tuple[Dict]: Tuple of 2 dicts.
            - Dict containing total market cap value for each sector.
            - Dict containing all the stocks in a given sector along with its
                market cap.
    """
    logger = logging.getLogger(__name__)
    df = df.sort_values(by="total_market_cap_in_cr", ascending=False)

    df = df.dropna(subset=["industry_info_sector"])
    df = df[
        [
            "comp_symbol",
            "total_market_cap_in_cr",
            "total_shares",
            "industry_info_sector",
        ]
    ]
    summed_df = df.groupby("industry_info_sector").sum()
    summed_df = summed_df.reset_index()

    res = {}
    for row in summed_df.itertuples(index=True):
        sector = row.industry_info_sector
        mcap = row.total_market_cap_in_cr
        res[sector] = mcap

    if dump_dir:
        pi_chart_path = os.path.join(dump_dir, "sectoral_pi_chart.png")
        create_pi_chart(res, "Sectoral market cap pi chart", pi_chart_path)
        logger.debug(f"Sectoral pi chart dumped at: {pi_chart_path}.")

    sectoral_data = {}
    for sector in res:
        filtered_df = df[df["industry_info_sector"] == sector][
            ["comp_symbol", "total_market_cap_in_cr"]
        ]
        filtered_df = filtered_df.rename(
            columns={
                "comp_symbol": "Company Symbol",
                "total_market_cap_in_cr": "Market Cap",
            }
        )
        sectoral_data[sector] = filtered_df.to_dict(orient="records")
        if dump_dir:
            sector_heatmap_path = os.path.join(dump_dir, f"heatmap_{sector}.png")
            create_sectoral_heatmap(sector, filtered_df, sector_heatmap_path, top=10)
            logger.debug(
                f"Sectoral heatmap chart for {sector} sector dumped at: {pi_chart_path}."
            )
    return res, sectoral_data


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
    parser.add_argument(
        "-l",
        "--log_level",
        default="info",
        type=str,
        help="Select log level for processing. E.g. info, debug.",
    )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Plot the pi chart and sectoral charts in output dir.",
    )
    args = parser.parse_args()

    setup_logger(args.log_level)
    res_df = fetch_data(args.num_threads, args.output_dir)
    sector_mcap_dict, sector_wise_mcap_comp_list = get_sectoral_market_cap(
        res_df, args.output_dir
    )


if __name__ == "__main__":
    main()
