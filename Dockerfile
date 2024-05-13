# Используем официальный образ Python 3.11
FROM python:3.11
LABEL authors="lon8"

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и файлы в рабочую директорию
COPY requirements.txt /app/
# Устанавливаем зависимости
RUN pip install -r requirements.txt

COPY . /app/



# Определяем команду для запуска приложения
CMD ["python", "main.py"]


