# Plano de validação

## Estado atual

O cenário `rs-urban-flood-synthetic-v1` é determinístico, agregado e inteiramente sintético. Ele possui quatro semanas de calibração, oito buckets de 30 minutos, três municípios e referência de início independente para cada município. Serve para verificar mecânica, não validade científica externa.

`python tools/verify.py` gera `artifacts/validation-report.json` comparando:

1. apenas picos de relatos;
2. apenas quedas de atividade;
3. combinação social por união;
4. combinação social corroborada por chuva.

Para cada variante são calculados precisão, revocação, F1, falsos positivos, tempo até detecção, erro no horário inicial, erro geográfico municipal, Brier de confiança, cobertura e buckets avaliados. `partial_source_recall` repete a avaliação removendo, separadamente, relatos, atividade digital e chuva. Isso é um ensaio determinístico de dropout, ainda não uma campanha multi-evento.

## Validação retrospectiva proposta

Usar as enchentes do RS de abril–maio de 2024 após aprovar e versionar arquivos concretos. Separar:

- **treino/baseline:** semanas históricas sem a janela de avaliação, estratificadas por município, dia e horário;
- **calibração:** eventos anteriores ou subconjunto territorial, usado para pesos/limiares;
- **avaliação cega:** municípios e janela RS-2024 não usados no ajuste.

Referência externa: S2iD/Atlas para área afetada e registros temporais físicos ANA/INMET/Cemaden licenciados; ANEEL como sinal negativo retrospectivo. A fonte usada como referência não pode participar do score avaliado. Registrar atraso conhecido, cobertura, versão/licença e incerteza de cada referência.

## Critérios antes de alegar utilidade

- Intervalos de confiança por evento e região, não apenas médias globais.
- Resultados por faixa de cobertura/conectividade e população, incluindo municípios sem fonte.
- Testes de madrugada, feriado, indisponibilidade de API, mudança de plataforma, bots e ausência parcial de uma ou mais fontes.
- Curva de calibração/confiabilidade, erro espacial em quilômetros e atraso com censura quando não há detecção.
- Revisão de falsos positivos por analistas e registro de discordância.
- Comparação com baseline ingênuo e publicação de falhas/limitações.

Nenhuma métrica sintética deve ser usada em divulgação como desempenho esperado em catástrofes reais.
