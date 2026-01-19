from dataclasses import dataclass, field
from datetime import datetime
import logging
import os

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import AssetClass, AssetExchange
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest

from dotenv import load_dotenv

import pandas as pd

from src.utils.common import chunk

logger = logging.getLogger(__name__)

_ = load_dotenv()


@dataclass
class AlpacaUtils:
    date: datetime
    timeframe: TimeFrame = TimeFrame.Day
    volume_percentile: float = 0.9
    asset_classes: list[AssetClass] = field(
        default_factory=lambda: [AssetClass.US_EQUITY]
    )
    exchanges: list[AssetExchange] = field(
        default_factory=lambda: [AssetExchange.NASDAQ]
    )
    symbols: list[str] = None
    tradable_only: bool = True
    use_cache: bool = True
    batch_size: int = 500

    def __post_init__(self):
        logger.info("Choosing symbols to request")
        if self.symbols is None:
            self.symbols = self.__get_volume_quantile_symbols()

    def __get_volume_quantile_symbols(self) -> list[str]:
        """
        The function retrieves all symbols from Alpaca API and then returns the subset of
        symbols with a trading volume superior to the requested quantile.
        """

        symbols = self.__get_assets_for_exchanges_and_classes()

        client = StockHistoricalDataClient(
            os.environ["ALPACA_PAPER_KEY"], os.environ["ALPACA_PAPER_SECRET_KEY"]
        )

        quantile_symbols = []

        for symbol_id, symbol_batch in enumerate(chunk(list(symbols), self.batch_size)):
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol_batch,
                timeframe=self.timeframe,
                start=self.date,
                end=self.date + pd.Timedelta(self.timeframe.value),
            )

            logger.info(
                f"Get all stock bars to filter by volume - Batch {symbol_id + 1} of {len(symbols)//self.batch_size+1}"
            )

            stock_bars = client.get_stock_bars(request_params)
            quantiles = stock_bars.df.volume.quantile([0.1 * i for i in range(0, 11)])

            quantile_symbols += (
                stock_bars.df[
                    stock_bars.df.volume > quantiles.loc[self.volume_percentile]
                ]
                .reset_index()
                .symbol.to_list()
            )

        return quantile_symbols

    def __get_assets_for_exchanges_and_classes(self) -> list[str]:
        """
        The function returns a list of symbols trading on the chosen exchanges
        and belonging to selected classes (e.g. US Equity or Crypto)
        """

        logger.info(
            "List all symbols available on Alpaca for selected exchanges and asset classes"
        )

        if self.tradable_only:
            logger.info("Collecting tradable assets only")

        trading_client = TradingClient(
            os.environ["ALPACA_PAPER_KEY"], os.environ["ALPACA_PAPER_SECRET_KEY"]
        )

        symbols = []
        for asset_class in self.asset_classes:
            for exchange in self.exchanges:

                file_name = f"data/cache/symbols_{asset_class.value.lower()}_{exchange.value.lower()}.txt"

                if self.use_cache and os.path.isfile(file_name):

                    logger.info(f"Loading assets from cache")
                    with open(file_name) as fp:
                        symbols_for_exchange_and_class = fp.read().splitlines()
                        symbols += symbols_for_exchange_and_class

                else:

                    logger.info(f"Requesting assets for class {asset_class}")

                    assets = trading_client.get_all_assets(
                        GetAssetsRequest(asset_class=asset_class, exchange=exchange)
                    )

                    symbols_for_exchange_and_class = []

                    for asset in assets:
                        if self.tradable_only and not asset.tradable:
                            continue
                        symbols_for_exchange_and_class.append(asset.symbol)

                    logger.info(f"Writing to cache {file_name}")

                    with open(file_name, "w") as fp:
                        for symbol in symbols_for_exchange_and_class:
                            fp.write(f"{symbol}\n")

                    symbols += symbols_for_exchange_and_class

        return symbols
