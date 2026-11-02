import os
import datetime
import random
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Matriz de temas técnicos B2B para rotación automática
TOPICS = [
    "Optimización de consultas SQL y gestión de índices en ERPs B2B",
    "Consumo de APIs REST externas mediante HttpClient y autenticación OAuth2",
    "Gestión de errores de concurrencia y bloqueos de tabla en bases de datos corporativas",
    "Diseño de Webhooks seguros para sincronización de datos entre sistemas",
    "Buenas prácticas de depuración de logs en entornos de producción B2B"
]

selected_topic = random.choice(TOPICS)
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

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

body = response.choices[0].message.content

# Formatear con el Front Matter que exige Hugo
markdown_content = f"""---
title: "{selected_topic}"
date: {date_str}
draft: false
tags: ["Sistemas", "B2B", "Integraciones"]
---

{body}
"""

# Guardar en la carpeta de contenidos
os.makedirs("content/posts", exist_ok=True)
filename = f"content/posts/post-{slug_date}-{random.randint(100, 999)}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"Artículo generado con éxito: {filename}")