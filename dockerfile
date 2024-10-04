# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (incluyendo git)
RUN apt-get update && apt-get install -y ffmpeg git libportaudio2 portaudio19-dev && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

# Copiar el código de la aplicación
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Copiar el archivo .env
COPY .env ./

# Exponer el puerto para FastAPI
EXPOSE 8000

# Comando para iniciar FastAPI
WORKDIR /app/backend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
