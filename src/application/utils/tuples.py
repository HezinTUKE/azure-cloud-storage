from typing import Any, NamedTuple


class AggSales(NamedTuple):
    groupby: list[str]
    agg: dict[str, Any]
    name: str
