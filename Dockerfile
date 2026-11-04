FROM python:3.13-slim

WORKDIR /app

# On copie requirements.txt seul d'abord : l'installation est mise en cache
# par Docker et ne se refait que si ce fichier change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Puis le code du projet
COPY . .

CMD ["python", "main.py"]
