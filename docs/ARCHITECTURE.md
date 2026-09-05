# Arquitetura do MVP

## Decisão e limites

O MVP é um monólito modular local: CPython 3.13 e sua biblioteca padrão no backend; ES modules, SVG e CSS no navegador; dados sintéticos agregados em memória. Não há banco, fila, credencial ou conteúdo social bruto. O mapa-base usa tiles remotos do OpenStreetMap e a tipografia usa Google Fonts, com fallback de fontes do sistema. O cenário e a análise independem desses serviços.

PostgreSQL/PostGIS é a evolução indicada quando houver malha municipal oficial, consultas espaciais e persistência concorrente. FastAPI e frontend TypeScript podem ser reavaliados quando contratos HTTP estáveis e uma equipe justificarem build/dependências. Kubernetes, microsserviços, streaming distribuído e aprendizado profundo são não objetivos.

## Fluxo

```text
Gerador sintético ─┐
                   ├─ documento comum ─ baseline ─ anomalias ─ fusão/propagação
Replay JSON ───────┘                                      │
                                                         HTTP local
                                                           │
                                              mapa SVG + timeline + explicação
```

## Módulos e interfaces

- **Adaptadores de fonte:** `build_demo_document()` e `load_replay(path)` retornam o mesmo documento normalizado. São duas implementações reais da seam de ingestão. Adaptadores futuros só entram habilitados com manifesto de licença/termos.
- **Módulo analítico:** `analyze_dataset(document)` é uma interface profunda: aprende baselines, enriquece a timeline, detecta pico/silêncio/misto, preserva evidências e produz hipótese/propagação. Não executa I/O.
- **Módulo de validação:** `evaluate_detectors(document)` compara quatro variantes contra a referência declarada.
- **Interface HTTP:** `create_server(address, document)` expõe resultados imutáveis para o replay carregado. `/api/scenario`, `/api/regions`, `/api/timeline`, `/api/anomalies`, `/api/hypotheses`, `/api/evidence`, `/api/sources`, `/api/health` e `/api/validation`.
- **Interface humana:** mapa-base geográfico com pontos aproximados do cenário, zoom e deslocamento, seleção de município, reprodução temporal e painel de medidas. `model.js` centraliza estados e projeção; `map.js` cuida da cartografia; `app.js` sincroniza controles e evidências. Entradas territoriais são tratadas como texto não confiável.
- **Exportação estática:** `tools/build_site.py` exporta a interface e apenas o cenário sintético padrão para `dist/`. `/scenario.json` é o contrato compartilhado entre o site estático e o servidor local. Os endpoints `/api/` continuam disponíveis no servidor Python.

## Modelo mínimo

O documento comum representa `Source`, `Observation` agregada, `Region` e frames. O resultado representa `RegionalBaseline`, `Anomaly`, `Evidence` e `DisasterHypothesis` conforme o glossário em `CONTEXT.md`.

- Horários são ISO-8601 UTC; o fuso original permanece em `metadata.timezone_original`.
- Toda medida declara `region_id`, métrica, fonte, natureza do dado, proveniência, precisão/confiança territorial e política de retenção.
- Conteúdo original não existe na demonstração; apenas contagens agregadas.
- `data_nature` é `real`, `simulated`, `mixed` ou `inferred`; inferência nunca é apresentada como observação.
- Baseline v1 usa média e desvio por município, métrica, dia da semana e horário; amostra pequena, feriados, sazonalidade e população conectada ainda são limitações explícitas.
- O detector exige |desvio padronizado| ≥ 2; chuva sozinha não produz hipótese. Pesos configurados no código são explicados por evidência e ainda não calibrados externamente.
- Propagação usa o primeiro bucket anômalo de cada município, centroide e distância geodésica; só estima com inícios distintos e informa intervalo heurístico. Não é modelo hidrológico.

## Confiabilidade e observabilidade

Replay é determinístico e idempotente: o mesmo documento produz a mesma saída. Arquivos são limitados a 10 MiB e validados antes de uso. O estado de cada fonte participa da confiança e aparece em `/api/health`; uma fonte degradada reduz contribuição, mas sua falha não é convertida em “silêncio territorial”. Retentativas e ingestão ao vivo ficam no futuro adaptador, onde devem ser instrumentadas por fonte sem alterar o módulo analítico.

## Evolução segura

1. Substituir geometria esquemática por malha IBGE versionada e atribuída.
2. Persistir o documento comum em PostGIS mantendo a interface analítica.
3. Adicionar primeiro um adaptador de arquivo físico licenciado (ANA/ANEEL), com fixture contratual e sincronização de correções.
4. Só então avaliar fontes sociais, após RIPD, base legal, termos, TTL, exclusão e limiar de agregação aprovados.
