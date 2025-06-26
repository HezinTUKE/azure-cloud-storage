import os
from io import BytesIO

from fastapi import UploadFile
from pandas import DataFrame
from sqlalchemy.ext.asyncio import AsyncSession

from application.dataclasses.file_metadata_dtc import FileMetadataDTC
from application.managers.sales_manager import SalesManager
from application.models import FileMetadata
from application.models.base import with_session
from application.services.azure_storage_service import AzureStorageService
from application.utils.tuples import AggSales


class UploadHandler:
    @classmethod
    def nt_func_mapping(cls) -> list[tuple]:
        agg_sales_per_region_and_product = AggSales(
            groupby=["product", "region", "date"], agg={"units_sold": "sum", "unit_price": "sum"}, name="products_by_region.csv"
        )

        agg_sales_per_user = AggSales(
            groupby=["salesperson", "region", "date"], agg={"units_sold": "sum", "unit_price": "sum"}, name="sellers_by_region.csv"
        )

        return [
            (agg_sales_per_region_and_product, SalesManager.process_sales),
            (agg_sales_per_user, SalesManager.process_sales),
        ]

    @classmethod
    @with_session(retries=1)
    async def upload_file_handle(cls, file: UploadFile, session: AsyncSession):
        """
        Function stores file in cloud and stores metadata of file in DB
        :param file: file which will be stored
        :param session: session to work with DB
        """
        attributes = {"file_name": file.filename, "file_size": file.size, "extension": os.path.splitext(file.filename)[1]}
        metadata_dtc = FileMetadataDTC(**attributes)
        metadata_dtc.path = os.path.join(metadata_dtc.file_metadata_id, metadata_dtc.file_name)
        azure_storage = await AzureStorageService.config(blob_name=metadata_dtc.path)
        saved_blob = await azure_storage.save_csv_blob(uploaded_file=file.file)
        if not saved_blob:
            return False

        metadata_dtc.uploaded_at = int(saved_blob.get("date").timestamp())

        aggregated_csvs: list[FileMetadataDTC] = await cls.upload_aggregated_csvs(file, metadata_dtc.file_metadata_id)
        aggregated_csvs.append(metadata_dtc)

        db_models = [FileMetadata(**dtc.model_dump()) for dtc in aggregated_csvs]
        session.add_all(db_models)
        await session.commit()
        return True

    @classmethod
    async def upload_aggregated_csvs(cls, file: UploadFile, parent_id: str) -> list[FileMetadataDTC]:
        csv_file_in_bytes = await SalesManager.file_to_bytes(file)
        func_result: list[FileMetadataDTC] = []
        for agg, func in cls.nt_func_mapping():
            csv_file_in_bytes.seek(0)
            result: DataFrame | dict[str, DataFrame] = await func(csv_file_in_bytes, agg)
            if isinstance(result, DataFrame):
                file_name = os.path.join(parent_id, "other", agg.name)
                func_result.append(await cls.store_aggregated_csv(file_name, result))
            else:
                for key, value in result.items():
                    key = "_".join(str(k).lower() for k in key) if isinstance(key, list) or isinstance(key, tuple) else key.lower()
                    file_name = os.path.join(parent_id, key.lower(), agg.name)
                    func_result.append(await cls.store_aggregated_csv(file_name, value))
        csv_file_in_bytes.close()
        return func_result

    @classmethod
    async def store_aggregated_csv(cls, file_name: str, df: DataFrame) -> FileMetadataDTC:
        azure_storage = await AzureStorageService.config(blob_name=file_name)
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        saved_blob = await azure_storage.save_csv_blob(uploaded_file=buffer)
        dtc = cls.create_dtc_model(
            file_name=file_name,
            uploaded_at=int(saved_blob.get("date").timestamp()),
            file_size=int(buffer.getbuffer().nbytes)
        )
        buffer.close()

        return dtc

    @classmethod
    def create_dtc_model(cls, file_name: str, uploaded_at: int, file_size: int) -> FileMetadataDTC:
        return FileMetadataDTC(
            **{
                "file_name": file_name.split("/")[-1],
                "file_size": file_size,
                "extension": os.path.splitext(file_name)[1],
                "path": file_name,
                "uploaded_at": uploaded_at,
            }
        )
