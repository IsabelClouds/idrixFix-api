# 1. Usar una imagen base de Python oficial y ligera
FROM python:3.12-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# ==================== INICIO DE LA MODIFICACIÓN ====================
# 3. Instalar dependencias del sistema para el controlador ODBC de SQL Server
#    - Se instalan certificados, curl y gnupg.
#    - Se descarga la clave GPG de Microsoft y se guarda en el formato correcto en /usr/share/keyrings.
#    - Se crea el archivo de repositorio apuntando a la clave descargada.
#    - Finalmente, se instala el controlador.
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
# ===================== FIN DE LA MODIFICACIÓN ======================

# 4. Copiar solo el archivo de dependencias primero para aprovechar el caché de Docker
COPY requirements.txt .

# 5. Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar todo el código del proyecto al contenedor
COPY . .

# 7. Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8020"]