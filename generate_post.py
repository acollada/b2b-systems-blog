import os
import datetime
import random
from google import genai

print(">>> [1/6] Verificando clave de API...")
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Error crítico: La variable GEMINI_API_KEY no está definida.")

print(">>> [2/6] Inicializando cliente de Google GenAI...")
client = genai.Client(api_key=api_key)

TOPICS = [
    "Optimización de consultas SQL y gestión de índices en ERPs B2B",
    "Consumo de APIs REST externas mediante HttpClient y autenticación OAuth2",
    "Gestión de errores de concurrencia y bloqueos de tabla en bases de datos corporativas",
    "Diseño de Webhooks seguros para sincronización de datos entre sistemas",
    "Buenas prácticas de depuración de logs en entornos de producción B2B"
]

selected_topic = random.choice(TOPICS)
print(f">>> [3/6] Tema seleccionado: {selected_topic}")

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

print(">>> [4/6] Enviando petición al modelo gemini-3.8-flash...")
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
)
print(">>> [5/6] Respuesta recibida correctamente.")

body = response.text

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

print(f">>> [6/6] Guardando archivo en {filename}...")
with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print("¡Proceso completado con éxito!")