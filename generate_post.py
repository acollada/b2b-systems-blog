import os
import datetime
import random
import json
import urllib.request
import urllib.error

print(">>> [1/4] Verificando clave de API...")
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Error crítico: La variable GEMINI_API_KEY no está definida.")

TOPICS = [
    "Optimización de consultas SQL y gestión de índices en ERPs B2B",
    "Consumo de APIs REST externas mediante HttpClient y autenticación OAuth2",
    "Gestión de errores de concurrencia y bloqueos de tabla en bases de datos corporativas",
    "Diseño de Webhooks seguros para sincronización de datos entre sistemas",
    "Buenas prácticas de depuración de logs en entornos de producción B2B"
]

selected_topic = random.choice(TOPICS)
print(f">>> [2/4] Tema seleccionado: {selected_topic}")

date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
slug_date = datetime.date.today().isoformat()

prompt = f"""
Actúa como un Arquitecto de Software B2B Senior. Escribe un artículo técnico completo y práctico en español sobre: "{selected_topic}".

Estructura requerida:
1. Requisitos previos y contexto técnico.
2. Paso a paso de resolución o implementación (listas numeradas).
3. Ejemplo de código bien comentado.
4. Buenas prácticas para evitar errores comunes.

Formato de salida: Devuelve ÚNICAMENTE el contenido en Markdown técnico, sin introducciones vacías.
"""

# Endpoint REST oficial y estable de Gemini 1.5 Flash
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    url, 
    data=data, 
    headers={"Content-Type": "application/json"}, 
    method="POST"
)

print(">>> [3/4] Enviando petición HTTP a Gemini API...")
try:
    # Timeout de 30 segundos para evitar bloqueos infinitos
    with urllib.request.urlopen(req, timeout=30) as response:
        res_body = json.loads(response.read().decode("utf-8"))
        body = res_body["candidates"][0]["content"]["parts"][0]["text"]
except urllib.error.HTTPError as e:
    error_detail = e.read().decode("utf-8")
    print(f">>> [ERROR] Fallo HTTP {e.code}: {error_detail}")
    raise SystemExit(1)
except Exception as e:
    print(f">>> [ERROR] Fallo de conexión: {e}")
    raise SystemExit(1)

print(">>> [4/4] Respuesta recibida y procesada con éxito.")

markdown_content = f"""---
title: "{selected_topic}"
date: {date_str}
draft: false
tags: ["Sistemas", "B2B", "Integraciones"]
---

{body}
"""

os.makedirs("content/posts", exist_ok=True)
filename = f"content/posts/post-{slug_date}-{random.randint(100, 999)}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"Archivo guardado correctamente en: {filename}")