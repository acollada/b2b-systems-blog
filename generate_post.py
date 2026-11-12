import datetime
import os
import random
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

print(">>> [1.5/3] Obteniendo modelos disponibles en Groq...")
try:
  models_response = client.models.list()
  available_models = [m.id for m in models_response.data]

  # Selección dinámica priorizando modelos Llama estables
  selected_model = None
  for pref in [
      "llama-3.3-70b",
      "llama-3.1-70b",
      "llama-3.1-8b",
      "llama3",
      "llama",
  ]:
    match = next((m for m in available_models if pref in m), None)
    if match:
      selected_model = match
      break

  if not selected_model and available_models:
    selected_model = available_models[0]
  elif not selected_model:
    selected_model = "llama-3.3-70b-versatile"
except Exception as e:
  print(
      f"Aviso al listar modelos ({e}), recurriendo a modelo por defecto."
  )
  selected_model = "llama-3.3-70b-versatile"

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
        " transaccionales de Business Central",
    ),
]

selected_topic = random.choice(TOPICS)
print(f">>> [2/3] Tema seleccionado: {selected_topic}")

date_str = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)
slug_date = datetime.date.today().isoformat()

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
    max_tokens=3000,
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

os.makedirs("content/posts", exist_ok=True)
filename = f"content/posts/post-{slug_date}-{random.randint(100, 999)}.md"

with open(filename, "w", encoding="utf-8") as f:
  f.write(markdown_content)

print(f"¡Artículo generado y guardado con éxito en {filename}!")
