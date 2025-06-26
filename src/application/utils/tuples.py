from typing import NamedTuple, Any


class AggSales(NamedTuple):
    groupby: list[str]
    agg: dict[str, Any]
    name: str
