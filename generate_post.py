import os
import datetime
import random
import json
import urllib.request
import urllib.error
import time

print(">>> [1/3] Verificando credenciales de API...")
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Error crítico: La variable GEMINI_API_KEY no está definida en los secretos.")

TOPICS = [
    "Optimización de consultas SQL y gestión de índices en ERPs B2B",
    "Consumo de APIs REST externas mediante HttpClient y autenticación OAuth2",
    "Gestión de errores de concurrencia y bloqueos de tabla en bases de datos corporativas",
    "Diseño de Webhooks seguros para sincronización de datos entre sistemas",
    "Buenas prácticas de depuración de logs en entornos de producción B2B"
]

selected_topic = random.choice(TOPICS)
print(f">>> Tema seleccionado: {selected_topic}")

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

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
payload = {"contents": [{"parts": [{"text": prompt}]}]}
data = json.dumps(payload).encode("utf-8")

req = urllib.request.Request(
    url, 
    data=data, 
    headers={"Content-Type": "application/json"}, 
    method="POST"
)

# Parámetros de resiliencia ante picos de tráfico (503 / 429)
max_retries = 5
backoff_base = 5  # Segundos base para el incremento exponencial
body = None

print(">>> [2/3] Conectando con Gemini 3.8 Flash (con reintentos automáticos)...")
for attempt in range(max_retries):
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            body = res_body["candidates"][0]["content"]["parts"][0]["text"]
            break
    except urllib.error.HTTPError as e:
        error_detail = e.read().decode("utf-8")
        print(f"[Intento {attempt + 1}/{max_retries}] Fallo HTTP {e.code}: {error_detail}")
        
        if e.code in [503, 429] and attempt < max_retries - 1:
            sleep_time = backoff_base * (2 ** attempt)  # 5s, 10s, 20s, 40s...
            print(f"Servidor ocupado. Reintentando automáticamente en {sleep_time} segundos...")
            time.sleep(sleep_time)
            continue
        raise SystemExit(f"Error crítico HTTP {e.code}: {error_detail}")
    except Exception as ex:
        print(f"[Intento {attempt + 1}/{max_retries}] Error de conexión: {ex}")
        if attempt < max_retries - 1:
            time.sleep(5)
            continue
        raise

if not body:
    raise SystemExit("Error crítico: No se pudo generar contenido tras agotar los reintentos.")

print(">>> [3/3] Contenido generado con éxito. Guardando archivo...")

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