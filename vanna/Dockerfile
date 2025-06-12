# vanna/Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# 设置环境变量：指定 Flask 应用入口
ENV FLASK_APP=app:flask_app
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 8084

CMD ["python", "app.py"]

