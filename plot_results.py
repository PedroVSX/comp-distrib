"""
plot_results.py — Gera gráficos de barras dos resultados do Locust

Métricas:
  - p95: percentil 95 de tempo de resposta (ms)
  - Taxa de falha: (falhas / total) * 100 (%)

Gráficos gerados (18 no total):
  Grupo 1 — Eixo X = usuários, barras = tamanho de página, um por instância (6)
  Grupo 2 — Eixo X = tamanho de página, barras = usuários, um por instância (6)
  Grupo 3 — Eixo X = instâncias, barras = usuários, um por tamanho de página (6)

Uso:
  pip install pandas matplotlib
  python plot_results.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = "./volumes/locust/results"
OUTPUT_DIR  = "./volumes/locust/graficos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

INSTANCES = [1, 2, 3]

# Usuários por cenário (leve, médio, pesado)
SCENARIO_USERS = {
    "scenario1": [10, 100, 3000],
    "scenario2": [10, 100, 750],
    "scenario3": [10, 100, 3000],
    "hybrid":    [10, 100, 800],
}

SCENARIOS = {
    "scenario1": "Imagem 1MB",
    "scenario2": "Texto 400KB",
    "scenario3": "Imagem 300KB",
}

# Rótulos dos níveis de carga (leve, médio, pesado)
USER_LABELS = ["Leve", "Médio", "Pesado"]

METRICS = {
    "95%":          "Percentil 95 de Resposta (ms)",
    "failure_rate": "Taxa de Falha (%)",
}

# Cores
PAGE_COLORS = ["#a8c8e8", "#f5c87a", "#f4a0a0"]   # azul, amarelo, rosa
USER_COLORS = ["#b5d5b5", "#a8c8e8", "#f5c87a"]   # verde, azul, amarelo

# ─── Leitura dos CSVs ─────────────────────────────────────────────────────────
def load_metric(scenario, users, instances, metric):
    path = os.path.join(RESULTS_DIR, f"{scenario}_u{users}_i{instances}_stats.csv")
    if not os.path.exists(path):
        print(f"  [AVISO] Não encontrado: {path}")
        return 0
    df  = pd.read_csv(path)
    row = df[df["Name"] == "Aggregated"]
    if row.empty:
        return 0
    row = row.iloc[0]
    if metric == "failure_rate":
        total = row["Request Count"]
        fails = row["Failure Count"]
        return round((fails / total * 100) if total > 0 else 0, 2)
    return row[metric]

# ─── Função de plot ───────────────────────────────────────────────────────────
def plot_grouped_bar(ax, x_labels, series, series_labels, colors, ylabel, title):
    n_groups = len(x_labels)
    n_series = len(series)
    width    = 0.22
    x        = np.arange(n_groups)

    for idx, (vals, label, color) in enumerate(zip(series, series_labels, colors)):
        offset = (idx - n_series / 2 + 0.5) * width
        bars   = ax.bar(x + offset, vals, width, label=label,
                        color=color, edgecolor="white", linewidth=0.8)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(vals) * 0.02,
                        f"{val:.1f}", ha="center", va="bottom",
                        fontsize=7, color="#444")

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.legend(fontsize=8, framealpha=0.7)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: {path}")

# ─── Grupo 1: eixo X = usuários, barras = tamanho de página ──────────────────
# Usa os usuários do scenario1 como referência para o eixo X (leve/médio/pesado)
print("\nGrupo 1 — Eixo X: usuários | Barras: tamanho de página")
for metric, ylabel in METRICS.items():
    for n_inst in INSTANCES:
        fig, ax = plt.subplots(figsize=(8, 5))
        series, labels = [], []
        for (sc_key, sc_label), color in zip(SCENARIOS.items(), PAGE_COLORS):
            users = SCENARIO_USERS[sc_key]
            vals  = [load_metric(sc_key, u, n_inst, metric) for u in users]
            series.append(vals)
            labels.append(sc_label)

        # Rótulos mostram leve/médio/pesado com os valores reais de cada cenário
        x_labels = [
            f"Leve\n(s1:{SCENARIO_USERS['scenario1'][0]}, s2:{SCENARIO_USERS['scenario2'][0]}, s3:{SCENARIO_USERS['scenario3'][0]})",
            f"Médio\n(s1:{SCENARIO_USERS['scenario1'][1]}, s2:{SCENARIO_USERS['scenario2'][1]}, s3:{SCENARIO_USERS['scenario3'][1]})",
            f"Pesado\n(s1:{SCENARIO_USERS['scenario1'][2]}, s2:{SCENARIO_USERS['scenario2'][2]}, s3:{SCENARIO_USERS['scenario3'][2]})",
        ]

        plot_grouped_bar(
            ax,
            x_labels      = x_labels,
            series        = series,
            series_labels = labels,
            colors        = PAGE_COLORS,
            ylabel        = ylabel,
            title         = f"{ylabel}\n{n_inst} instância(s) — por nível de carga",
        )
        ax.set_xlabel("Nível de carga (número de usuários)", fontsize=10)
        safe = metric.replace("/", "_per_").replace("%", "pct").replace(" ", "_")
        save(fig, f"g1_{safe}_i{n_inst}_x_usuarios.png")

# ─── Grupo 2: eixo X = tamanho de página, barras = níveis de carga ────────────
print("\nGrupo 2 — Eixo X: tamanho de página | Barras: nível de carga")
for metric, ylabel in METRICS.items():
    for n_inst in INSTANCES:
        fig, ax = plt.subplots(figsize=(8, 5))
        series, labels = [], []
        for level_idx, (level_label, color) in enumerate(zip(USER_LABELS, USER_COLORS)):
            vals = [
                load_metric(sc_key, SCENARIO_USERS[sc_key][level_idx], n_inst, metric)
                for sc_key in SCENARIOS
            ]
            series.append(vals)
            labels.append(level_label)

        plot_grouped_bar(
            ax,
            x_labels      = list(SCENARIOS.values()),
            series        = series,
            series_labels = labels,
            colors        = USER_COLORS,
            ylabel        = ylabel,
            title         = f"{ylabel}\n{n_inst} instância(s) — por tamanho de página",
        )
        ax.set_xlabel("Tamanho da página", fontsize=10)
        safe = metric.replace("/", "_per_").replace("%", "pct").replace(" ", "_")
        save(fig, f"g2_{safe}_i{n_inst}_x_paginas.png")

# ─── Grupo 3: eixo X = instâncias, barras = níveis de carga ──────────────────
print("\nGrupo 3 — Eixo X: instâncias | Barras: nível de carga")
for metric, ylabel in METRICS.items():
    for sc_key, sc_label in SCENARIOS.items():
        fig, ax = plt.subplots(figsize=(8, 5))
        series, labels = [], []
        for level_idx, (level_label, color) in enumerate(zip(USER_LABELS, USER_COLORS)):
            u    = SCENARIO_USERS[sc_key][level_idx]
            vals = [load_metric(sc_key, u, i, metric) for i in INSTANCES]
            series.append(vals)
            labels.append(f"{level_label} ({u} usuários)")

        plot_grouped_bar(
            ax,
            x_labels      = [str(i) for i in INSTANCES],
            series        = series,
            series_labels = labels,
            colors        = USER_COLORS,
            ylabel        = ylabel,
            title         = f"{ylabel}\n{sc_label} — por número de instâncias",
        )
        ax.set_xlabel("Número de instâncias", fontsize=10)
        safe_metric = metric.replace("/", "_per_").replace("%", "pct").replace(" ", "_")
        save(fig, f"g3_{safe_metric}_{sc_key}_x_instancias.png")

print(f"\n✓ Todos os gráficos salvos em: {OUTPUT_DIR}")
total = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")])
print(f"  Total de gráficos: {total}")