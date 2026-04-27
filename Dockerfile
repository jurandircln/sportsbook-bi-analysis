# Imagem base Python 3.12 slim
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar uv para gerenciamento de dependências
RUN pip install uv

# Copiar arquivos de configuração de dependências
COPY pyproject.toml .

# Instalar dependências do projeto via uv
RUN uv sync --no-dev

# Copiar o código-fonte
COPY src/ ./src/

# Expor porta do Streamlit
EXPOSE 8501

# Comando padrão: iniciar o dashboard Streamlit
CMD ["uv", "run", "streamlit", "run", "src/dashboard/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
