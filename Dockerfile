FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/
COPY tests/ ./tests/
COPY Makefile .

# Criar diretório para logs e artefatos
RUN mkdir -p /tmp/dev_trooper /app/artifacts

# Expor porta (se necessário para webhooks)
EXPOSE 8000

# Comando padrão
CMD ["python", "-m", "app.main"]
