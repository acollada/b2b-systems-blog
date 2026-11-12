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

print(
    ">>> [1.5/3] Descubriendo y ordenando modelos de chat estables en Groq..."
)

# Lista base de respaldo en orden de preferencia
fallback_models = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

candidate_models = []
try:
  models_response = client.models.list()
  available_ids = [m.id for m in models_response.data]

  # Filtrar modelos de chat aptos (excluyendo guards, embeds, audio, etc.)
  chat_models = [
      m
      for m in available_ids
      if not any(
          x in m.lower()
          for x in [
              "guard",
              "embed",
              "whisper",
              "vision",
              "moderation",
              "prompt",
          ]
      )
  ]

  # Priorizar los que contengan 'llama' o 'mixtral'
  sorted_chat = sorted(
      chat_models,
      key=lambda x: (
          0
          if "llama" in x.lower()
          else (1 if "mixtral" in x.lower() else 2)
      ),
  )

  # Combinar descubiertos con respaldos garantizando unicidad
  candidate_models = list(dict.fromkeys(sorted_chat + fallback_models))
except Exception as e:
  print(
      f"Aviso al listar modelos dinámicamente ({e}), usando lista de respaldo"
      " predefinida."
  )
  candidate_models = fallback_models

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
timestamp_suffix = int(time.time() * 1000)

prompt = f"""Escribe un artículo técnico avanzado y detallado en formato Markdown sobre el desarrollo en Microsoft Dynamics 365 Business Central (lenguaje AL) centrado en el siguiente tema: "{selected_topic}".

Estructura obligatoria:
1. Requisitos previos, contexto técnico y arquitectura en Business Central.
2. Paso a paso de implementación en AL con listas numeradas.
3. Bloque de código AL de ejemplo comentado y optimizado (usando sintaxis limpia y buenas prácticas de AL).
4. Buenas prácticas de rendimiento, escalabilidad y errores comunes a evitar."""

print(">>> [3/3] Ejecutando inferencia con sistema de reintento por modelo...")
response = None
used_model = None

for model_candidate in candidate_models:
  try:
    print(f"-> Probando modelo: {model_candidate}")
    response = client.chat.completions.create(
        model=model_candidate,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
    )
    used_model = model_candidate
    print(f"✓ Éxito con el modelo: {used_model}")
    break
  except Exception as e:
    print(
        f"x Falló el modelo {model_candidate} (Error: {str(e).split(' - ')[0]})."
        " Probando siguiente..."
    )

if not response:
  raise ValueError(
      "Error crítico: Ninguno de los modelos candidatos pudo completar la"
      " inferencia en Groq."
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
