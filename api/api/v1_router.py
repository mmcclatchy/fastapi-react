import glob
import importlib
import os

from fastapi import APIRouter


V1Router = APIRouter(prefix="/v1")

"""
Programmatically import router from all files within v1 subdirectory
NOTE:  the variable 'router' must be defined in every file within the v1 subdirectory
"""

# Current Working Directory
cwd = os.getcwd()

# Get all files within v1 subdirectory
module_paths = glob.glob(f"/{cwd}/api/v1/*.py")

for module_path in module_paths:
    module_name = module_path.split("/")[-1].split(".")[0]

    # Ignore __init__.py
    if not module_name.startswith("_"):
        # Import module
        module = importlib.import_module(f"api.v1.{module_name}")

        # Add router to V1Router
        V1Router.include_router(module.router)
