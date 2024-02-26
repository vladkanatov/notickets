# migrate.py

from sqlalchemy import create_engine
from database.models.main_models import Base

# Замените 'sqlite:///example.db' на ваше фактическое соединение с базой данных
engine = create_engine('sqlite:///example.db')

# Создание таблицы
Base.metadata.create_all(engine)