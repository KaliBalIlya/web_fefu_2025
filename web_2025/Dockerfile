# ~/web_2025/web_2025/Dockerfile
###########
# builder #
###########
FROM python:3.11 AS builder

ARG PIP_NO_CACHE_DIR=1
ENV PIP_NO_CACHE_DIR=${PIP_NO_CACHE_DIR}
WORKDIR /app

# Системные зависимости для сборки пакетов (если нужны)
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements заранее для кэширования слоёв
COPY requirements.txt /app/requirements.txt

# Создаём venv и используем его pip для установки зависимостей
RUN python -m venv /opt/venv
RUN /opt/venv/bin/python -m pip install --upgrade pip

# Устанавливаем зависимости из requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Диагностика: показать python и pip и pip freeze (это поможет в логах)
RUN /opt/venv/bin/python -c "import sys; print('PYTHON:', sys.executable)"
RUN /opt/venv/bin/pip --version
RUN /opt/venv/bin/pip freeze || true

# Копируем весь проект
COPY . /app

# Убедимся, что Django установлен — если нет, ставим явно (fallback)
RUN /opt/venv/bin/python - <<'PY'
try:
    import django
    print("Django found:", django.get_version())
except Exception:
    import sys, subprocess
    print("Django not found, installing Django...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Django"])
    import django
    print("Django installed:", django.get_version())
PY

# Настройка для collectstatic
ENV DJANGO_SETTINGS_MODULE=web_2025.settings_production
ENV PATH="/opt/venv/bin:$PATH"

# Собираем статику
RUN /opt/venv/bin/python manage.py collectstatic --noinput

###########
#  prod   #
###########
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# runtime deps (pg client)
RUN apt-get update && apt-get install -y libpq5 postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создаём непривилегированного пользователя
RUN groupadd -r django && useradd -r -g django django

# Копируем venv и собранный проект из builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

RUN chown -R django:django /app

USER django

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "web_2025.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
