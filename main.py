from datetime import datetime
import logging

from alpaca.trading.enums import AssetExchange

from src.utils.alpaca_utils import AlpacaUtils


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    alpaca_utils = AlpacaUtils(
        datetime(2025, 12, 30), exchanges=[AssetExchange.NASDAQ, AssetExchange.NYSE]
    )
    print(len(alpaca_utils.symbols))

if __name__ == "__main__":
    setup_logging()
    main()
