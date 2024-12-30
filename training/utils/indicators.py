import pandas as pd
from collections.abc import Callable


class ComputeRegistry:
    _computes = {}
    @classmethod
    def register(cls, indictor_type: str, compute: Callable):
        cls._computes[indictor_type] = compute

    @classmethod
    def compute(cls, indicator_type: str, data: pd.DataFrame, n_points: int) -> pd.DataFrame:
        return cls._computes[indicator_type](data, n_points)


def register_compute(indicator_types: list[str]) -> Callable:
    def inner(fn: Callable) -> Callable:
       for indicator in indicator_types:
            ComputeRegistry.register(indicator, fn)
       return fn
    return inner


@register_compute(['Momentum A', 'Momentum B'])
def compute_momentum(data: pd.DataFrame, n_points: int) -> pd.DataFrame:
    return data.rolling(n_points).mean().dropna()


@register_compute(['Rolling Std'])
def compute_rolling_std(data: pd.DataFrame, n_points: int) -> pd.DataFrame:
    return data.rolling(n_points).std().dropna()

@register_compute(['Momentum Exponential A'])
def compute_momentum_exponential(data: pd.DataFrame, npoint: int) -> pd.DataFrame:
    data['Short_MA'] = data['Close'].ewm(span=npoint).mean().dropna()
    return data

@register_compute(['Momentum Exponential B'])
def compute_momentum_exponential(data: pd.DataFrame, npoint: int ) -> pd.DataFrame:
    data['Long_MA'] = data['Close'].ewm(span=npoint).mean().dropna()
    return data

@register_compute(['Bollinger Bands'])
def compute_bollinger_bands(data: pd.DataFrame, n_points: int) -> pd.DataFrame:
    momentum = compute_momentum(data, n_points)
    std = compute_rolling_std(data, n_points)
    lower_band = momentum - 2 * std
    upper_band = momentum + 2 * std
    return momentum.join(
        lower_band.join(upper_band, lsuffix='_lower', rsuffix='_upper'),
        lsuffix='_momentum'
    )

