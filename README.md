# Trabalho 3 — Testes de Carga com Locust

## Estrutura de pastas

```
projeto/
├── docker-compose.yml
├── run_tests.sh
└── volumes/
    ├── mysql/                  ← criado automaticamente
    ├── nginx/
    │   └── nginx.conf
    └── locust/
        ├── locustfile.py
        └── results/            ← CSVs gerados aqui
```

---

## Passo 1 — Organizar os arquivos

```bash
mkdir -p volumes/nginx volumes/locust/results volumes/mysql
cp nginx.conf    volumes/nginx/nginx.conf
cp locustfile.py volumes/locust/locustfile.py
```

---

## Passo 2 — Criar os posts no WordPress

Antes de rodar os testes, você precisa criar **3 posts** no WordPress:

| Post | Conteúdo | ID esperado |
|------|----------|-------------|
| Cenário 1 | Imagem ~1 MB | 1 (padrão) |
| Cenário 2 | Texto ~400 KB | 2 (padrão) |
| Cenário 3 | Imagem ~300 KB | 3 (padrão) |

### Como criar um post com imagem grande
1. Acesse `http://localhost/wp-admin`
2. Vá em **Posts > Adicionar novo**
3. Adicione uma imagem em destaque com o tamanho pedido
4. Publique e anote o ID (aparece na URL: `post=X`)

### Se os IDs forem diferentes
Edite o `locustfile.py` e ajuste as variáveis no topo:
```python
POST_IMAGE_1MB   = 1   # ID real do seu post
POST_TEXT_400KB  = 2
POST_IMAGE_300KB = 3
```

### Como gerar texto de 400 KB
Use o site https://loremipsum.io/ e gere texto suficiente
(400.000 caracteres ≈ 400 KB), ou rode:
```bash
python3 -c "print('Lorem ipsum ' * 35000)" > texto400kb.txt
```
Cole o conteúdo no editor do WordPress.

---

## Passo 3 — Subir a infraestrutura

```bash
# Sobe tudo (1 instância do WordPress por padrão)
docker compose up -d mysql wordpress nginx

# Aguarde ~30s para o WordPress inicializar
# Verifique em http://localhost
```

---

## Passo 4 — Rodar os testes automaticamente

```bash
chmod +x run_tests.sh
./run_tests.sh
```

O script vai:
1. Para cada combinação de instâncias (1, 2, 3) → escala o WordPress
2. Para cada número de usuários (10, 100, 1000) → roda o Locust headless
3. Salva 4 CSVs por teste na pasta `volumes/locust/results/`

**Duração total estimada:** ~27 testes × 60s = ~30 minutos

---

## Passo 5 — Verificar os CSVs

```bash
ls volumes/locust/results/
```

Você verá arquivos como:
```
scenario1_u10_i1_stats.csv
scenario1_u10_i1_stats_history.csv
scenario1_u10_i1_failures.csv
scenario1_u10_i1_exceptions.csv
scenario1_u100_i1_stats.csv
...
scenario3_u1000_i3_stats.csv
```

### Principais métricas nos CSVs

| Arquivo | O que contém |
|---------|-------------|
| `_stats.csv` | Média, mediana, p95, p99, req/s por endpoint |
| `_stats_history.csv` | Métricas ao longo do tempo (para gráficos de linha) |
| `_failures.csv` | Requisições que falharam |

---

## Ajustes opcionais

### Aumentar o tempo de cada teste
No `run_tests.sh`, altere:
```bash
RUN_TIME="120s"   # 2 minutos por teste
```

### Rodar um teste manual (com UI)
```bash
docker compose up locust
# Acesse http://localhost:8089
```

### Escalar manualmente
```bash
docker compose up -d --scale wordpress=3
```

---

## Dica: gerar gráficos com Python

Depois de coletar os CSVs, você pode plotar os gráficos pedidos pelo professor:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Exemplo: tempo de resposta médio — cenário 1
dados = {}
for instancias in [1, 2, 3]:
    for usuarios in [10, 100, 1000]:
        df = pd.read_csv(f"volumes/locust/results/scenario1_u{usuarios}_i{instancias}_stats.csv")
        # Filtra só o agregado total
        row = df[df["Name"] == "Aggregated"]
        dados[(usuarios, instancias)] = row["Average Response Time"].values[0]

# Montar o gráfico de barras agrupadas (igual ao do professor)
# ... (ver exemplo completo no plot_results.py)
```
