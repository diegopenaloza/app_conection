# Usa la imagen base oficial de Python
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requerimientos al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos al contenedor
COPY . .

# Instala netcat-openbsd en lugar de netcat
RUN apt-get update && apt-get install -y netcat-openbsd

# Expone el puerto en el que se ejecutará la aplicación
# EXPOSE 8000

# Comando para ejecutar la aplicación cuando se inicie el contenedor
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

ENV NEO4J_HOST='my-neo4j-container' 
ENV NEO4J_PORT="7687"
ENV NEO4J_USER="neo4j"
ENV NEO4J_PASSWORD="12345678"

# Agrega la lógica de espera antes de ejecutar la aplicación
CMD echo "Waiting for Neo4j to start..." && \
    while ! nc -z $NEO4J_HOST $NEO4J_PORT; do sleep 1; done && \
    echo "Neo4j is ready! Starting the application..." && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
