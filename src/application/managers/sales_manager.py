from io import StringIO

import pandas as pd
from fastapi import UploadFile
from pandas import DataFrame

from application.utils.tuples import AggSales

CHUNK = 1000


class SalesManager:
    @classmethod
    async def process_csv(cls, file: UploadFile):
        content = await file.read()
        str_content = StringIO(content.decode("utf-8"))
        df = pd.read_csv(str_content)
        return df

    @classmethod
    async def process_sales(cls, csv_content: StringIO, agg_sales: AggSales) -> DataFrame | dict[str, DataFrame] | dict[tuple, DataFrame]:
        result = []
        if "date" in agg_sales.groupby:
            groupby_cols = [col if col != "date" else "year" for col in agg_sales.groupby]
        else:
            groupby_cols = agg_sales.groupby

        for chunk in pd.read_csv(csv_content, chunksize=CHUNK, header=0):
            chunk: DataFrame

            if "date" in chunk.columns:
                chunk["date"] = pd.to_datetime(chunk["date"], dayfirst=True, format="%m/%d/%Y")
                chunk["year"] = chunk["date"].dt.year

            result.append(chunk.groupby(groupby_cols).agg(agg_sales.agg))

        aggregated_df = pd.concat(result).groupby(groupby_cols).agg(agg_sales.agg)

        if "year" in groupby_cols and "region" in groupby_cols:
            year_level = groupby_cols.index("year")
            region_level = groupby_cols.index("region")

            groups = {(year, region): group_df for (year, region), group_df in aggregated_df.groupby(level=[year_level, region_level])}
            return groups
        elif "region" in groupby_cols:
            region_level = groupby_cols.index("region")
            groups = {region: group_df for region, group_df in aggregated_df.groupby(level=region_level)}
            return groups

        else:
            return aggregated_df

    @classmethod
    async def file_to_bytes(cls, file: UploadFile) -> StringIO:
        await file.seek(0)
        content = await file.read()
        return StringIO(content.decode("utf-8"))
