from io import BytesIO

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient

from application import config_azure


class AzureStorageService:
    def __init__(self, container_client: ContainerClient, blob_name: str):
        self.blob_name = blob_name
        self.blob_client = container_client.get_blob_client(blob=blob_name)

    @classmethod
    async def config(cls, blob_name: str):
        connection_str = f"""DefaultEndpointsProtocol={config_azure.get("protocol")};AccountName={config_azure.get("account_name")};AccountKey={config_azure.get("account_key")};EndpointSuffix={config_azure.get("endpoint_suffix")}"""
        container_name = config_azure.get("additional_data", {}).get("container_name")
        blob_client = BlobServiceClient.from_connection_string(conn_str=connection_str)

        try:
            container_client = blob_client.create_container(container_name)
        except Exception:
            container_client = blob_client.get_container_client(container_name)

        return cls(container_client, blob_name)

    async def save_csv_blob(self, uploaded_file: BytesIO) -> dict | None:
        try:
            uploaded_file.seek(0)
            return self.blob_client.upload_blob(data=uploaded_file, overwrite=False)
        except Exception as ex:
            raise ex
