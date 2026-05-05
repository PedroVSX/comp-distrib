#!/usr/bin/env bash
# =============================================================================
# run_tests.sh — 36 testes no total:
#   3 cenários individuais × 3 usuários × 3 instâncias = 27 testes
#   1 cenário híbrido      × 3 usuários × 3 instâncias =  9 testes
#   Total: 36 _stats.csv
#
# Uso: chmod +x run_tests.sh && ./run_tests.sh
# =============================================================================

set -uo pipefail

INSTANCES=(1 2 3)
RESULTS_DIR="./volumes/locust/results"
RUN_TIME="60s"

mkdir -p "$RESULTS_DIR"

# Cada cenário tem seus próprios usuários e spawn rates
declare -A SCENARIO_USERS
declare -A SCENARIO_SPAWNS

SCENARIO_USERS["scenario1"]="10 100 3000"
SCENARIO_SPAWNS["scenario1"]="10 10 200"

SCENARIO_USERS["scenario2"]="10 100 750"
SCENARIO_SPAWNS["scenario2"]="10 10 75"

SCENARIO_USERS["scenario3"]="10 100 3000"
SCENARIO_SPAWNS["scenario3"]="10 10 200"

SCENARIO_USERS["hybrid"]="10 100 800"
SCENARIO_SPAWNS["hybrid"]="10 10 80"

SCENARIOS=("scenario1" "scenario2" "scenario3" "hybrid")

echo "=============================================="
echo " Trabalho 3 — Testes de Carga com Locust"
echo " Instâncias: ${INSTANCES[*]}"
echo " Duração   : $RUN_TIME por teste"
echo " Total     : 36 testes"
echo "=============================================="
echo ""

TOTAL=0
FAILED=0

for SCENARIO in "${SCENARIOS[@]}"; do
  for N_INSTANCES in "${INSTANCES[@]}"; do

    echo "──────────────────────────────────────────────"
    echo "▶ Escalando WordPress para $N_INSTANCES instância(s)..."
    docker compose up -d --scale wordpress="$N_INSTANCES" --no-recreate nginx mysql wordpress
    echo "  Aguardando WordPress estabilizar (15s)..."
    sleep 15

    USERS_LIST=(${SCENARIO_USERS[$SCENARIO]})
    SPAWNS_LIST=(${SCENARIO_SPAWNS[$SCENARIO]})

    for idx in "${!USERS_LIST[@]}"; do
      N_USERS="${USERS_LIST[$idx]}"
      SPAWN_RATE="${SPAWNS_LIST[$idx]}"
      TOTAL=$((TOTAL + 1))

      echo ""
      echo "  [Teste $TOTAL] Cenário=$SCENARIO | Usuários=$N_USERS | Spawn=$SPAWN_RATE | Instâncias=$N_INSTANCES"

      docker compose run --rm \
        -e SCENARIO="$SCENARIO" \
        locust \
        -f /mnt/locust/locustfile.py \
        --headless \
        --host http://nginx \
        --users "$N_USERS" \
        --spawn-rate "$SPAWN_RATE" \
        --run-time "$RUN_TIME" \
        --csv "/mnt/locust/results/${SCENARIO}_u${N_USERS}_i${N_INSTANCES}" \
      && echo "  ✓ Teste concluído." \
      || { echo "  ✗ Teste FALHOU."; FAILED=$((FAILED + 1)); }

      echo "  Pausa de 5s entre testes..."
      sleep 5
    done

  done
done

# Remove arquivos desnecessários, mantém só os _stats.csv
rm -f "$RESULTS_DIR"/*_failures.csv
rm -f "$RESULTS_DIR"/*_exceptions.csv

echo ""
echo "=============================================="
echo " Concluído!"
echo " Testes realizados : $TOTAL"
echo " Falhas            : $FAILED"
CSV_COUNT=$(ls "$RESULTS_DIR"/*.csv 2>/dev/null | wc -l || echo 0)
echo " Total de CSVs     : $CSV_COUNT"
echo "=============================================="