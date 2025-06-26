import os

import yaml

with open(f"{os.getcwd()}/application/config.yml", "r") as file:
    config_data = yaml.safe_load(file)

config_db = config_data.get("database", {})
config_azure = config_data.get("azure", {})
