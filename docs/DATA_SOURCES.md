# Fontes de dados

**Consulta:** 30 de agosto de 2026. **Natureza:** análise técnica preliminar, não aconselhamento jurídico.

A pesquisa detalhada, com acesso, retenção, exclusão, custos, privacidade e links oficiais por fonte, está em [research/SOURCE_RESEARCH.md](research/SOURCE_RESEARCH.md). Nenhuma conta, credencial, aceite, scraping ou coleta pessoal foi realizada.

## Decisão resumida

| Fonte | Uso candidato | Acesso permitido | Situação no MVP |
|---|---|---|---|
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

O evento retrospectivo recomendado é a enchente do Rio Grande do Sul de abril–maio de 2024, cruzando S2iD/Atlas (área declarada), ANA/HidroWeb e arquivos meteorológicos licenciados (cronologia física) e ANEEL (interrupções retrospectivas). Antes de baixar ou versionar qualquer arquivo, é obrigatório registrar a licença do recurso concreto. Por isso, o MVP entregue usa apenas uma referência sintética e não afirma validação externa.
