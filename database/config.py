
from models.main_models import metadata
from sqlalchemy import engine_from_config


config = {
    "sqlalchemy.url": "mysql://lon8:132465-Cs@localhost/eventservice",
    "script_location": "/",
}

engine = engine_from_config(config, prefix="sqlalchemy.")
target_metadata = metadata
