import yfinance as yf
from pathlib import Path


def fetch_raw_etf_data(
    ticker: str,
    start_date: str = "2018-01-01",
    output_dir: str = "data/raw"
):
    """
    Fetch raw ETF price data and save it locally as CSV.
    """

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Download data
    df = yf.download(ticker, start=start_date)

    if df.empty:
        raise ValueError(f"No data downloaded for ticker: {ticker}")

    # Save raw dataset
    file_path = output_path / f"{ticker}_raw_prices.csv"
    df.to_csv(file_path)

    print(f"Raw dataset saved to: {file_path}")


if __name__ == "__main__":
    # Change ticker if needed
    fetch_raw_etf_data(
        ticker="SPY",
        start_date="2018-01-01"
    )
