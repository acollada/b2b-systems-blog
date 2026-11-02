import os
import datetime
import random
from openai import OpenAI

print(">>> [1/3] Verificando credenciales de Groq...")
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("Error crítico: La variable GROQ_API_KEY no está definida en los secretos.")

# Cliente OpenAI apuntando al endpoint accesible de Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)

TOPICS = [
    "Optimización de consultas SQL y gestión de índices en ERPs B2B",
    "Consumo de APIs REST externas mediante HttpClient y autenticación OAuth2",
    "Gestión de errores de concurrencia y bloqueos de tabla en bases de datos corporativas",
    "Diseño de Webhooks seguros para sincronización de datos entre sistemas",
    "Buenas prácticas de depuración de logs en entornos de producción B2B"
]

selected_topic = random.choice(TOPICS)
print(f">>> [2/3] Tema seleccionado: {selected_topic}")

date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
slug_date = datetime.date.today().isoformat()

prompt = f"""Escribe un artículo técnico detallado y completo en formato Markdown sobre el siguiente tema: "{selected_topic}".

Estructura obligatoria:
1. Requisitos previos y contexto técnico.
2. Paso a paso de implementación con listas numeradas.
3. Bloque de código de ejemplo comentado.
4. Buenas prácticas y errores comunes a evitar."""

print(">>> [3/3] Solicitando inferencia a Llama-3.3-70B vía Groq...")
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=3000
)

body = response.choices[0].message.content

if not body or len(body.strip()) < 100:
    raise ValueError("Error crítico: El modelo devolvió una respuesta vacía.")

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

print(f"¡Artículo generado y guardado con éxito en {filename}!")