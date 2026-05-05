"""
locustfile.py — Testes de carga para o Trabalho 3

Cenários (variável de ambiente SCENARIO):
  scenario1 — Blog post com imagem ~1 MB  (individual)
  scenario2 — Blog post com texto  ~400 KB (individual)
  scenario3 — Blog post com imagem ~300 KB (individual)
  hybrid    — Todos os posts de uma vez    (híbrido)
"""

import os
from locust import HttpUser, between, task

_SCENARIO = os.getenv("SCENARIO", "scenario1")

# ─── Cenário 1: imagem ~1 MB ──────────────────────────────────────────────────
class Scenario1User(HttpUser):
    wait_time = between(1, 3)

    @task
    def post_image_1mb(self):
        self.client.get("/wp-content/uploads/2026/05/pexels-cristianrossaoutdoor-12421204.jpg", name="[S1] Post imagem 1MB")


# ─── Cenário 2: texto ~400 KB ─────────────────────────────────────────────────
class Scenario2User(HttpUser):
    wait_time = between(1, 3)

    @task
    def post_text_400kb(self):
        self.client.get("/2026/05/04/titulo-3/", name="[S2] Post texto 400KB")


# ─── Cenário 3: imagem ~300 KB ────────────────────────────────────────────────
class Scenario3User(HttpUser):
    wait_time = between(1, 3)

    @task
    def post_image_300kb(self):
        self.client.get("/wp-content/uploads/2026/05/dan-begel-1arqRdBRYY-unsplash.jpg", name="[S3] Post imagem 300KB")


# ─── Cenário Híbrido: todos os posts de uma vez ───────────────────────────────
class HybridUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def post_image_1mb(self):
        self.client.get("/2026/05/04/titulo-2/", name="[H] Post imagem 1MB")

    @task(2)
    def post_text_400kb(self):
        self.client.get("/2026/05/04/titulo-3/", name="[H] Post texto 400KB")

    @task(1)
    def post_image_300kb(self):
        self.client.get("/2026/05/04/titulo/", name="[H] Post imagem 300KB")


# ─── Seleção do cenário via variável de ambiente ─────────────────────────────
if _SCENARIO == "scenario2":
    del Scenario1User, Scenario3User, HybridUser
elif _SCENARIO == "scenario3":
    del Scenario1User, Scenario2User, HybridUser
elif _SCENARIO == "hybrid":
    del Scenario1User, Scenario2User, Scenario3User
else:
    # scenario1 (padrão)
    del Scenario2User, Scenario3User, HybridUser
