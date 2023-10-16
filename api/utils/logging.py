import logging

from utils.settings import settings


logger = logging.getLogger()
logger.setLevel(logging.DEBUG if settings.env == "dev" else logging.INFO)

# Create a console handler and set the level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if settings.env == "dev" else logging.INFO)

# Create a formatter and attach it to the handler
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)
