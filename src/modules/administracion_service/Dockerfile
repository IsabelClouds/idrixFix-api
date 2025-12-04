# Dockerfile para el servicio de autenticación
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para el controlador ODBC de SQL Server
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    apt-transport-https \
    gcc g++ \
    unixodbc-dev \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements desde la raíz del proyecto
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Exponer el puerto del servicio
EXPOSE 8004

# Variable de entorno para el servicio
ENV PYTHONPATH=/app

# Comando para ejecutar el servicio de autenticación
CMD ["uvicorn", "src.modules.administracion_service.main:app", "--host", "0.0.0.0", "--port", "8004"]
