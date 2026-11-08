
# Imagen base de Python
FROM python:3.13-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar las dependencias
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para la base de datos persistente
RUN mkdir -p /data

# Puerto que utilizará Flask
EXPOSE 5000

# Ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app"]
