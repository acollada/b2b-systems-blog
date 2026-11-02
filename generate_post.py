import os
import datetime
import random
import json
import urllib.request
import urllib.error

print(">>> [1/4] Verificando PAT de GitHub...")
gh_pat = os.environ.get("GH_PAT")
if not gh_pat:
    raise ValueError("Error crítico: La variable GH_PAT no está definida en los secretos.")

# Endpoint oficial de Azure AI Inference para GitHub Models
url = "https://models.inference.ai.azure.com/chat/completions"

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

payload = {
    "model": "Meta-Llama-3.3-70B-Instruct",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 3000
}

headers = {
    "Authorization": f"Bearer {gh_pat}",
    "Content-Type": "application/json"
}

print(">>> [3/4] Generando contenido mediante endpoint oficial...")
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode("utf-8")
        print(f"DEBUG - Respuesta cruda: {res_body[:300]}")
        data = json.loads(res_body)
except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8")
    raise ValueError(f"Error HTTP del servidor ({e.code}): {error_body}")
except json.JSONDecodeError:
    raise ValueError(f"El servidor no devolvió un JSON válido. Respuesta recibida: '{res_body}'")

if "choices" in data and len(data["choices"]) > 0:
    body = data["choices"][0]["message"]["content"]
else:
    raise ValueError(f"Estructura JSON inesperada: {data}")

if not body or len(body.strip()) < 100 or body.strip().startswith("OK"):
    raise ValueError(f"Error crítico: El modelo devolvió contenido inválido: '{body}'")

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