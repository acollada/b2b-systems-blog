import os
import datetime
import random
from openai import OpenAI

print(">>> [1/4] Verificando PAT de GitHub...")
gh_pat = os.environ.get("GH_PAT")
if not gh_pat:
    raise ValueError("Error crítico: La variable GH_PAT no está definida en los secretos.")

# Endpoint oficial de GitHub Models
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=gh_pat,
)

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

# Instrucción de sistema estricta para evitar respuestas de cortesía o "OK"
system_instruction = (
    "Eres un arquitecto de software B2B especializado en documentación técnica. "
    "Tu única función es redactar artículos técnicos completos en formato Markdown. "
    "Está estrictamente prohibido responder con acuses de recibo, confirmaciones como 'OK' o saludos. "
    "Genera siempre el contenido del artículo de forma íntegra."
)

user_prompt = f"""
Escribe un artículo técnico detallado en Markdown sobre el siguiente tema: "{selected_topic}".

Estructura obligatoria que debe contener el texto:
1. Requisitos previos y contexto técnico.
2. Paso a paso de implementación (con listas numeradas).
3. Bloque de código comentado.
4. Buenas prácticas y errores comunes.
"""

print(">>> [3/4] Generando contenido con gpt-4o...")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.3,  # Menor temperatura para evitar respuestas erráticas o conversacionales
    max_tokens=3000
)

# Extracción robusta de la respuesta
if hasattr(response, "choices") and response.choices:
    body = response.choices[0].message.content
elif isinstance(response, dict) and "choices" in response:
    body = response["choices"][0]["message"]["content"]
else:
    body = str(response)

# Validación estricta para cortar la ejecución si vuelve a fallar
if not body or len(body.strip()) < 100 or body.strip().startswith("OK"):
    raise ValueError(f"Error crítico: El modelo devolvió una respuesta inválida: '{body}'")

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

print(f">>> [4/4] Guardando archivo en {filename}...")
with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print("¡Artículo generado y guardado con éxito!")