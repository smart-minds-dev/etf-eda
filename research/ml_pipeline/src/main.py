from typing import List, Optional, Any
from data_ingestion.fetch_data import DataFetch
from preprocessing.runner import DataPreprocess
from transformation.runner import DataTransform
from transformation.transformers.base import TransformConfig

def main(tickers, start_date, end_date: Optional[Any] = None):
    fetcher = DataFetch()
    fetched_data = fetcher.fetch_data(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date
    )

    preprocessor = DataPreprocess()
    cleaned_data = preprocessor.preprocess(df=fetched_data)

    transformer = DataTransform(transform_config=TransformConfig)
    transformed_data = transformer.transform(df=cleaned_data)
    transformed_data.to_csv("output.csv", index=False)

if __name__ == "__main__":
    TICKERS = ["SPY", "VTI", "SCHD", "BND", "SPLV", 
            "VCN.TO", "ZAG.TO", "VDY.TO", "VFV.TO", "XIC.TO"]
    START_DATE = "2018-01-01"
    main(tickers=TICKERS, start_date=START_DATE)
