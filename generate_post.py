import datetime
import glob
import os
import random
import time
from openai import OpenAI

print(">>> [1/3] Verificando credenciales de Groq...")
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
  raise ValueError(
      "Error crítico: La variable GROQ_API_KEY no está definida en los"
      " secretos."
  )

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)

print(">>> [1.5/3] Seleccionando modelo de chat estable en Groq...")
# Modelos preferidos orientados a generación de texto y código en orden de prioridad
PREFERRED_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
]
selected_model = "llama-3.3-70b-versatile"  # Fallback seguro por defecto

try:
  models_response = client.models.list()
  available_ids = [m.id for m in models_response.data]

  # Buscar primero entre los modelos preferidos conocidos
  found = False
  for model_candidate in PREFERRED_MODELS:
    if model_candidate in available_ids:
      selected_model = model_candidate
      found = True
      break

  # Si no está en la lista preferida, buscar cualquier modelo de chat válido excluyendo guards/embeds
  if not found:
    chat_models = [
        m
        for m in available_ids
        if any(k in m for k in ["70b", "8b", "inst", "vers"])
        and not any(
            x in m.lower()
            for x in ["guard", "embed", "whisper", "vision", "moderation"]
        )
    ]
    if chat_models:
      selected_model = chat_models[0]
except Exception as e:
  print(
      f"Aviso al listar modelos ({e}), usando modelo por defecto:"
      f" {selected_model}"
  )

print(f">>> Modelo seleccionado: {selected_model}")

TOPICS = [
    (
        "Optimización de rendimiento en extensiones de AL mediante QueryObjects y"
        " filtrado eficiente"
    ),
    (
        "Gestión avanzada de eventos y suscripciones (Event Subscribers) en"
        " Business Central"
    ),
    (
        "Implementación de llamadas HTTP externas y manejo de errores con"
        " HttpClient en AL"
    ),
    (
        "Patrones de diseño y control transaccional robusto en extensiones de"
        " Business Central"
    ),
    (
        "Optimización de consultas masivas y prevención de bloqueos en tablas"
        " transaccionales de Business Central"
    ),
]

print(">>> [2/3] Comprobando posts existentes para evitar duplicados...")
existing_titles = set()
os.makedirs("content/posts", exist_ok=True)

for filepath in glob.glob("content/posts/*.md"):
  try:
    with open(filepath, "r", encoding="utf-8") as f:
      content = f.read()
      for line in content.splitlines():
        if line.startswith("title:"):
          title_val = line.split(":", 1)[1].strip().strip('"')
          existing_titles.add(title_val)
  except Exception:
    pass

# Filtrar temas que ya hayan sido publicados
available_topics = [t for t in TOPICS if t not in existing_titles]

if not available_topics:
  print(">>> Aviso: Todos los temas ya han sido publicados. Reiniciando ciclo.")
  available_topics = TOPICS

selected_topic = random.choice(available_topics)
print(f">>> Tema seleccionado: {selected_topic}")

date_str = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)
slug_date = datetime.date.today().isoformat()
timestamp_suffix = int(
    time.time() * 1000
)  # Sufijo único para evitar colisiones de ficheros

prompt = f"""Escribe un artículo técnico avanzado y detallado en formato Markdown sobre el desarrollo en Microsoft Dynamics 365 Business Central (lenguaje AL) centrado en el siguiente tema: "{selected_topic}".

Estructura obligatoria:
1. Requisitos previos, contexto técnico y arquitectura en Business Central.
2. Paso a paso de implementación en AL con listas numeradas.
3. Bloque de código AL de ejemplo comentado y optimizado (usando sintaxis limpia y buenas prácticas de AL).
4. Buenas prácticas de rendimiento, escalabilidad y errores comunes a evitar."""

print(f">>> [3/3] Solicitando inferencia a {selected_model} vía Groq...")
response = client.chat.completions.create(
    model=selected_model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=2048,
)

body = response.choices[0].message.content

if not body or len(body.strip()) < 100:
  raise ValueError("Error crítico: El modelo devolvió una respuesta vacía.")

markdown_content = f"""---
title: "{selected_topic}"
date: {date_str}
draft: false
tags: ["Business Central", "AL", "Desarrollo", "Optimización"]
---

{body}
"""

filename = f"content/posts/post-{slug_date}-{timestamp_suffix}.md"

with open(filename, "w", encoding="utf-8") as f:
  f.write(markdown_content)

print(f"¡Artículo generado y guardado con éxito en {filename}!")
