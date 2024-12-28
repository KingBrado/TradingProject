from abc import ABC, abstractmethod
from typing import Type, Callable
import numpy as np
from numpy.typing import DTypeLike
import pandas as pd
from itertools import product


class Strategy(ABC):

    def __init__(self, params: dict):
        self.params = params

    @abstractmethod
    def fit(self, X, y):
        ...
    
    @abstractmethod
    def predict(self, X):
        ...


class StrategyRegistry:

    _strategies = {}
    @classmethod
    def register(cls, strategy_choice: str, strategy: Type[Strategy]):
        cls._strategies[strategy_choice] = strategy

    @classmethod
    def get_strategy(cls, strategy_choice: str, params: dict) -> Type[Strategy]:
        return cls._strategies[strategy_choice](params)


def register_strategy(strategy_choice: str) -> Callable:
    def inner(cls: Type[Strategy]) -> Callable:
        StrategyRegistry.register(strategy_choice, cls)
        return cls
    return inner


@register_strategy('crossover')
class Crossover(Strategy):

    def __init__(self, params: dict):
        super().__init__(params)
        self._m = None
        self._n = None

    def fit(self, X: pd.Series, y: np.array=None) -> np.array:
        m_range = self.params['m_range']
        n_range = self.params['n_range']
        max_ret = float("-inf")
        max_m = -1
        max_n = -1
        for m, n in product(range(*m_range), range(*n_range)):
            if m < n:
                self._m = m
                self._n = n
                ret = self.predict(X)
                if ret > max_ret:
                    max_m = m
                    max_n = n
                    max_ret = ret
        self._m = max_m
        self._n = max_n
        print(self)
    
    def predict(self, X) -> DTypeLike:
        if self._m is None or self._n is None:
            raise ValueError("You need to call fit before predict")
        momentum_1 = X.rolling(self._m).mean()
        momentum_2 = X.rolling(self._n).mean()
        data = pd.DataFrame(
            data={
                "price": X,
                "momentum_1": momentum_1,
                "momentum_2": momentum_2
            },
            index=momentum_1.index
        ).dropna()
        buy_signal = momentum_1 > momentum_2
        data['buy_signal'] = buy_signal.shift(1) - buy_signal
        data = data[data.buy_signal != 0]
        if data.iloc[0]['buy_signal'] == 1:
            data = data.iloc[1:]
        if data.iloc[-1]['buy_signal'] == -1:
            data = data.iloc[:-1]
        buy_price = data.loc[data.buy_signal == -1, 'price']
        sell_price = data.loc[data.buy_signal == 1, 'price']           
        log_ret = np.sum(np.log(sell_price.values) - np.log(buy_price.values))
        return log_ret
    

    def __repr__(self):
        return f"{self.__class__.__name__}(m={self._m}, n={self._n})"


if __name__ == '__main__':
    import yfinance as yf
    data = yf.download('INTC', period='2y', interval='1d', multi_level_index=False)
    adj_close_old = data['Adj Close']
    crossover = Crossover({
        'm_range': list(range(2, 10)),
        'n_range': list(range(5, 20))
    })
    crossover.fit(adj_close_old)

    print(np.exp(crossover.predict(adj_close_old)) - 1)
