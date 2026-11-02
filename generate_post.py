import os
import datetime
import random
from openai import OpenAI

print(">>> [INICIO] Arrancando generador de posts...")

# 1. Verificación de credenciales
gh_pat = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
if not gh_pat:
    raise ValueError("Error crítico: No se encontró la variable GH_PAT ni GITHUB_TOKEN.")
print(">>> [1/4] Token verificado correctamente.")

# Endpoint oficial de GitHub Models (Azure AI Inference)
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
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

prompt = f"""Escribe un artículo técnico detallado y completo en formato Markdown sobre el siguiente tema: "{selected_topic}".

Estructura obligatoria:
1. Requisitos previos y contexto técnico.
2. Paso a paso de implementación con listas numeradas.
3. Bloque de código de ejemplo comentado.
4. Buenas prácticas y errores comunes a evitar."""

print(">>> [3/4] Solicitando inferencia al modelo (Meta-Llama-3.3-70B-Instruct)...")
response = client.chat.completions.create(
    model="Meta-Llama-3.3-70B-Instruct",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=3000
)

body = response.choices[0].message.content

if not body or len(body.strip()) < 100:
    raise ValueError(f"Error crítico: El modelo devolvió una respuesta vacía o inválida: '{body}'")

markdown_content = f"""---
title: "{selected_topic}"
date: {date_str}
draft: false
tags: ["Sistemas", "B2B", "Integraciones"]
---

{body}
"""

# Asegurar directorio y escritura física
output_dir = "content/posts"
os.makedirs(output_dir, exist_ok=True)
filename = f"{output_dir}/post-{slug_date}-{random.randint(100, 999)}.md"

print(f">>> [4/4] Escribiendo archivo físico en: {filename}")
with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_content)

# Verificación de que el archivo existe realmente
if os.path.exists(filename):
    print(f"¡Éxito! Archivo creado correctamente. Tamaño: {os.path.getsize(filename)} bytes.")
else:
    raise FileNotFoundError(f"Error crítico: No se pudo generar el archivo en {filename}")