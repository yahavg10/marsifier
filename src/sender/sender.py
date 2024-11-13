import io
import logging
import os
from typing import NoReturn, Callable

from PIL import Image
from fastapi import UploadFile
from requests import RequestException

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import default_send_fn
from src.sender.payload_methods import file_invoker
from src.utils.annotations import Inject

logger = logging.getLogger(name=os.getenv("ENV"))


def merge_files_endpoint(
        files: list[UploadFile]):
    temp_dir = "./temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    merged_content = [file[1].read() for file in files]
    content = b''.join(merged_content)
    image = Image.open(io.BytesIO(content))
    image.save(os.path.join(temp_dir, "test1.jpg"), format="JPEG")


@Inject("AppConfig")
def send(app_config: AppConfig, common_name: str, sender_type: str, payload_fn=file_invoker,
         send_method: Callable = default_send_fn) -> NoReturn:
    try:
        app_config.sender[sender_type]["params"]["common_name"] = common_name
        payload = payload_fn(**app_config.sender[sender_type]["params"])
        response = send_method(app_config.sender[sender_type]["endpoint"], files=payload)
        # response = send_method(app_config.sender[sender_type]["endpoint"], files=payload)
        logger.info(response)
    except RequestException as e:
        logger.warning(f"Error during request: {str(e)}")
