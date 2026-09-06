# Fontes de dados

**Consulta:** 30 de agosto de 2026. **Natureza:** análise técnica preliminar, não aconselhamento jurídico.

A pesquisa detalhada, com acesso, retenção, exclusão, custos, privacidade e links oficiais por fonte, está em [research/SOURCE_RESEARCH.md](research/SOURCE_RESEARCH.md). Nenhuma conta, credencial, aceite, scraping ou coleta pessoal foi realizada.

## Decisão resumida

| Fonte | Uso candidato | Acesso permitido | Situação no MVP |
|---|---|---|---|
| IODA / Georgia Tech | Conectividade estadual | API pública oficial; leitura local autorizada pelo usuário | **Integrada em /ioda.html** |
| Dataset sintético do projeto | Replay, baseline e validação | Geração local determinística | **Aprovada e ativa** |
| X API | Sinais sociais agregados | Apenas API/caso de uso oficialmente aprovados | **Experimental; desativada** |
| Bluesky/AT Protocol | Sinais sociais agregados | Endpoints/stream oficiais, sujeitos a termos e exclusões | **Experimental; desativada** |
| Mastodon | Sinais sociais agregados | API e política de cada instância | **Experimental; desativada** |
| INMET | Chuva/meteorologia | Arquivos públicos; API mediante solicitação | **Restrita por recurso** |
| Cemaden | Chuva, rios, radar, alertas | Download/formulário oficial; sem automação presumida | **Experimental** |
| INPE/CPTEC | Meteorologia/satélite | Coleções oficialmente abertas | **Restrita por coleção** |
| ANA/HidroWeb | Chuva, nível e vazão | Downloads abertos; API mediante solicitação | **Restrita; API experimental** |
| S2iD/Atlas | Referência histórica municipal | Consulta/export oficial | **Restrita à validação** |
| Defesa Civil Alerta/IDAP | Marcos oficiais históricos | Consulta pública; operação restrita | **Experimental/manual** |
| ANEEL | Interrupções retrospectivas | Download/API CKAN, ODbL | **Restrita à ODbL** |
| ONS | Carga macrorregional | Download/API CKAN, conjuntos CC BY | **Restrita e contextual** |
| Anatel | Qualidade/interrupções históricas | Exports oficiais por recurso | **Restrita; não tempo real** |
| OpenStreetMap data | Vias/rios/POIs | Extratos/APIs conforme ODbL | **Restrita à ODbL** |
| `tile.openstreetmap.org` | Basemap | Uso moderado conforme política | **Rejeitado como backend do MVP** |
| IBGE malha municipal | Limites/códigos municipais | Download oficial, edição conferida | **Aprovada, CC BY 4.0** |

## Regras de admissão

Uma fonte só sai de `experimental` quando um manifesto versionado registra proprietário, URL oficial, licença do recurso, termos da API, finalidade, atribuição, retenção, propagação de exclusões, limites/custos, data de conferência e responsável pela aprovação. “Público” ou “visível” não significa livre para armazenar ou redistribuir.

Falha de uma fonte é telemetria de saúde, não evidência automática de desastre. Conteúdo social bruto, autores e coordenadas residenciais não entram na demonstração. Adaptadores não aprovados devem usar a interface comum por fixture/replay.

## Caso histórico proposto

O evento retrospectivo recomendado é a enchente do Rio Grande do Sul de abril–maio de 2024, cruzando S2iD/Atlas (área declarada), ANA/HidroWeb e arquivos meteorológicos licenciados (cronologia física) e ANEEL (interrupções retrospectivas). Antes de baixar ou versionar qualquer arquivo, é obrigatório registrar a licença do recurso concreto. O replay de desastre permanece sintético; a consulta recente ao IODA não valida esse cenário.

## Registro IODA — 05/09/2026

- Proprietário: Georgia Tech Research Corporation; serviço IODA. [API oficial](https://api.ioda.inetintel.cc.gatech.edu/v2/).
- Recurso: região Rio de Janeiro, código IODA 499, resolvida via `/entities/query` com país BR; séries `/signals/raw/region/499` e `/outages/events`.
- Finalidade e autorização: consumidor solicitado explicitamente pelo usuário; leitura local de séries agregadas de conectividade. Nenhuma credencial ou aceite foi exigido nas chamadas verificadas.
- Atribuição: IODA / Georgia Tech na tela e link à região; campo copyright preservado nas séries e eventos.
- Direitos retornados: “This data is Copyright (c) 2021-2025 Georgia Tech Research Corporation. All Rights Reserved.” Não se atribui licença aberta aos dados nem licença do software da API a este consumidor independente.
- Retenção: cache em memória de cinco minutos; última coleta utilizável retida durante falhas até encerrar o processo. CLI grava o último snapshot no caminho escolhido, padrão `.cache/ioda/latest.json`. Sem versionamento automático de dados, redistribuição pública ou arquivo histórico contínuo.
- Exclusão: encerrar o servidor elimina cache em memória; usuário pode remover o arquivo local. A consulta não inclui autores, conteúdo pessoal ou coordenadas residenciais.
- Limites/custos: sem chave ou cobrança observada na consulta pública; sem garantia de cota contratual. Até três tentativas, resposta limitada a 5 MiB, cache compartilhado, 288 pontos solicitados por série e até 25 eventos. Resultado no limite é sinalizado como possivelmente truncado.
- Interpretação: cobertura estadual. Ausência e falha têm estados próprios; sem identificação municipal, contagem de pessoas ou confirmação de desastre.

## Registro RIPE Atlas e Cloudflare Radar — 05/09/2026

**RIPE Atlas / RIPE NCC.** [Catálogo e filtros](https://atlas.ripe.net/docs/apis/rest-api-manual/probes/listing-probes/), [resultados recentes](https://atlas.ripe.net/docs/apis/rest-api-reference/measurements/measurements_latest), [testes existentes](https://atlas.ripe.net/docs/getting-started/built-in-measurements/). Leitura local autorizada pelo usuário; acesso público verificado sem chave. Finalidade: amostras municipais de conectividade IPv4. Somente sondas explicitamente públicas. IPs, descrições e coordenadas de sondas são descartados na normalização; associação municipal aproximada com margem de exclusão de 1 km nas bordas. Cache em memória, removido ao encerrar o processo, sem arquivo histórico automático ou redistribuição de dataset bruto. Atribuição RIPE Atlas / RIPE NCC e links às sondas na interface. Acesso público não implica concessão de licença própria sobre os dados.

**Cloudflare Radar.** [Acesso](https://developers.cloudflare.com/radar/get-started/first-request/) e [ocorrências](https://developers.cloudflare.com/api/resources/radar/subresources/annotations/subresources/outages/methods/get/). Integração local autorizada; consumidor implementado, sem token disponível nesta sessão. A validação autenticada permanece pendente. Finalidade: relatos contextuais brasileiros dos últimos sete dias, com menções geográficas explícitas. Token somente no backend, escopo de leitura Radar conforme guia oficial; custo/cota contratual não aferidos. Limite local de 300 ocorrências por coleta. Texto limitado e URLs validadas; não inferir geografia de ASN. Cache em memória, sem persistência automática. Atribuição e links à fonte. Nenhum aceite ou publicação externa realizado.

**Malha municipal IBGE.** 92 municípios do RJ obtidos da API v3 de Malhas, qualidade mínima; nomes da API v1 de Localidades. Incorporada em `static/rio-municipalities.geojson`, com fonte e data registradas no arquivo. Limites simplificados e localização ofuscada das sondas restringem a precisão. Pontos não associados não são atribuídos ao município mais próximo.
