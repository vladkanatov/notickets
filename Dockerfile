# Используем официальный образ Python 3.11
FROM python:3.11
LABEL authors="lon8"

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и файлы в рабочую директорию
COPY requirements.txt /app/
COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Определяем команду для запуска приложения
CMD ["python", "main.py"]


