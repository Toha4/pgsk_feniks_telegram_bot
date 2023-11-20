FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Установка TZ
ENV TZ=Asia/Vladivostok

WORKDIR /telegram_bot

# Устанавливаем зависимости
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

# Копируем файлы и билд
COPY ./src ./

RUN chmod -R 777 ./