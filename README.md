# Pulso Territorial

**Conectividade, relatos e lacunas de observação em um mapa.**

Anteriormente chamado Mapa do Silêncio. O novo nome abrange os sinais observados e sua ausência, sem presumir a causa.

Mapa local do Rio de Janeiro com simulação de silêncio digital, conectividade estadual IODA e amostras municipais RIPE Atlas. O consumidor de ocorrências Cloudflare Radar depende de token. Não confirma desastres nem emite alertas.

## Requisitos

- Python 3.13 (validado com 3.13.7)
- Navegador moderno

Não há dependências PyPI/npm, banco ou credenciais para executar a demonstração. O navegador usa internet para a cartografia do OpenStreetMap e para as fontes Google Fonts; o cenário continua local e sintético. Sem rede, as observações e os controles continuam disponíveis, com aviso de mapa-base indisponível e fontes do sistema.

## Executar

```powershell
python run.py
```

Abra <http://127.0.0.1:8000>. Para outra porta:

```powershell
python run.py --port 8080
```

Para um replay JSON autorizado ou sintético:

```powershell
python run.py --replay caminho\cenario.json
```

Replay `real` ou `mixed` exige `metadata.usage_basis`; isso não substitui aprovação jurídica/privacidade nem aceita termos em nome do usuário.

## Verificar e reproduzir relatórios

```powershell
python tools/verify.py
```

O comando executa os testes Python (incluindo IODA e HTTP ponta a ponta), verifica que não há imports de pacotes externos, gera o relatório comparativo dos quatro detectores, o relatório de licenças e o SBOM SPDX.

Arquivos gerados:

- `artifacts/validation-report.json`
- `artifacts/license-report.json`
- `sbom.spdx.json`

## O que observar na demonstração

Selecione um município na lista ou no mapa. Arraste o mapa, use os botões de zoom e enquadramento ou navegue pelas setas do teclado. A linha do tempo permite avançar, voltar, reproduzir e alterar a velocidade entre 1×, 2× e 4×. A demonstração padrão cobre o estado do Rio de Janeiro e abre na sexta etapa, às 10:30 BRT. Rio de Janeiro, Petrópolis, Nova Friburgo, Campos dos Goytacazes, Cabo Frio e Angra dos Reis têm sinais sintéticos. O contorno estadual simplificado é do IBGE; isso não significa cobertura de todos os municípios.

O painel mostra a variação da atividade digital, observado/esperado, chuva e relatos do município selecionado. Verde representa atividade esperada, âmbar destaca silêncio e azul indica pico de relatos. Fontes indisponíveis e dados insuficientes têm estados separados. As conexões e os números mostram a ordem de detecção do silêncio, sem estimar trajetória física. Os pontos são aproximados; os círculos não delimitam áreas afetadas.

## Organização da interface

- `static/app.js`: seleção, evidências e controles de replay.
- `static/map.js`: cartografia, deslocamento, zoom e marcadores.
- `static/model.js`: interpretação dos estados e projeção geográfica.
- `static/styles.css` e `static/index.html`: apresentação responsiva.

Os arquivos estão em `src/mapa_silencio/`. Para verificar as regras da interface, execute `node --test tests/frontend.test.mjs` com Node.js 22 ou superior. Node não é necessário para executar o site local.

Para gerar a versão estática, execute `python tools/build_site.py`. O diretório `dist/` contém a interface e uma exportação somente do cenário sintético fluminense padrão. O servidor Python também entrega esse contrato em `/scenario.json`, preservando os endpoints `/api/` existentes.

## Documentação

- [Fontes de dados](docs/DATA_SOURCES.md) e [pesquisa primária](docs/research/SOURCE_RESEARCH.md)
- [Matriz de licenças](docs/LICENSE_MATRIX.md) e [decisão de licença](LICENSE-PROPOSAL.md)
- [Arquitetura](docs/ARCHITECTURE.md) e [glossário](CONTEXT.md)
- [Privacidade](docs/PRIVACY.md), [modelo de ameaças](docs/THREAT_MODEL.md) e [validação](docs/VALIDATION_PLAN.md)
- [Avisos de terceiros](THIRD_PARTY_NOTICES.md)

## Limitações materiais

Ainda não há validação de detecção com desastres históricos, persistência PostGIS, baseline sazonal, ingestão social ou detector de bots. A consulta real IODA e o contorno IBGE estão integrados; isso não valida as métricas sintéticas nem permite inferir perdas municipais.

## IODA: dados reais

Execute `python run.py` e abra <http://127.0.0.1:8000/ioda.html> ou **Dados reais · IODA** na navegação. A API pública respondeu sem chave na consulta de 05/09/2026. Nenhuma conta ou variável de ambiente é necessária.

O servidor resolve o estado do Rio de Janeiro no país BR e usa o código regional IODA 499 (não o código IBGE). Consulta as últimas 24 horas de BGP, sondagem ativa e telescópio de rede, além de até 25 eventos. A fonte externa permanece sujeita a atrasos e indisponibilidade.

- Endpoint: `GET /api/ioda`. Cache em memória compartilhado por cinco minutos. A página visível consulta nesse intervalo; não há coletor contínuo sem consultas.
- Até três tentativas por requisição, timeout de 12 segundos e espera limitada. Falha completa preserva a coleta anterior identificada como antiga, retorna HTTP 503 e permite nova tentativa após um minuto.
- Valores ausentes não viram zero. Atraso significa mais de 30 minutos ou três intervalos desde a última medição, o que for maior. É uma regra local de atualização, não detecção de interrupções.
- A variação compara o último valor com a mediana dos valores anteriores da janela, com pelo menos 13 pontos válidos. É descritiva, sem baseline sazonal ou probabilidade de desastre.
- Cobertura mede intervalos com dados, não população. A medição é estadual e não é atribuída aos municípios da simulação. IODA não mede posts do X ou causas de desastre.

Coleta avulsa:

```powershell
python tools/consume_ioda.py
python tools/consume_ioda.py --hours 48 --output .cache/ioda/48h.json
```

O padrão é `.cache/ioda/latest.json`, ignorado pelo Git. A escrita é atômica; uma coleta totalmente indisponível não sobrescreve o arquivo anterior. A tela mantém seu próprio cache em memória, independente desse arquivo.

Código: `src/mapa_silencio/ioda.py` (consumidor/cache), `server.py` (endpoint), `static/ioda-view.js` (interface). A exportação estática inclui a tela, mas precisa do servidor Python para consultar dados reais; sem o endpoint ela informa indisponibilidade.

Referência: [API oficial IODA](https://api.ioda.inetintel.cc.gatech.edu/v2/).

## Monitoramento local: RIPE Atlas e Cloudflare Radar

Abra <http://127.0.0.1:8000/monitoring.html>. A tela mostra os 92 municípios do RJ, com busca e seleção pelo mapa, e mantém cada fonte identificada.

**RIPE Atlas — ativo, sem chave.** O endpoint `GET /api/ripe` lê o catálogo público no retângulo do RJ, percorre as páginas e associa coordenadas aproximadas à malha IBGE. Pontos a menos de 1 km do limite municipal ou fora da malha não são associados. Sondas privadas são excluídas. Os marcadores representam resumos municipais, não os endereços das sondas.

São consultados resultados já existentes dos pings IPv4 1001 (K-root) e 1004 (F-root), para as sondas selecionadas, com busca nas últimas 24 horas. Nenhuma medição é criada e nenhum crédito é consumido para criar testes. Resultado de até 15 minutos conta como recente. A tela distingue sondas cadastradas, conexão com o Atlas, resultados recentes, perda de pacotes e RTT. “Com medição recente” significa existência de uma amostra, não internet normal no município. Os testes não cobrem IPv6 nem todos os provedores.

**Cloudflare Radar — consumidor pronto, ativação depende do token.** `GET /api/cloudflare` consulta ocorrências brasileiras dos últimos sete dias. Sem credencial retorna `not_configured`, sem inventar uma lista vazia. Menções explícitas ao RJ são separadas do contexto nacional; correspondência textual de município é aproximada. “Rio de Janeiro” isolado não é atribuído à capital. Um ASN não identifica um município. Há limite de três páginas de 100 eventos, com aviso de possível truncamento.

Configure a credencial somente no processo do servidor:

1. Siga o [guia oficial do Radar](https://developers.cloudflare.com/radar/get-started/first-request/) para criar um token com **Account → Radar → Read**.
2. Encerre a instância atual do servidor antes de usar a mesma porta.
3. No PowerShell, dentro do projeto, execute os comandos abaixo. O token é digitado em um campo oculto e não precisa ser enviado no chat ou salvo em arquivo.

```powershell
$radarToken = Read-Host "Token Cloudflare Radar" -AsSecureString
$env:CLOUDFLARE_API_TOKEN = [System.Net.NetworkCredential]::new("", $radarToken).Password
try { python run.py } finally { Remove-Item Env:CLOUDFLARE_API_TOKEN; $radarToken.Dispose() }
```

A API aceita o token por header no backend; ele não entra no HTML, JSON público, logs de erro ou exportação estática. Respostas 401/403 aparecem como indisponibilidade, sem divulgar o conteúdo retornado pelo serviço.

Cada fonte mantém cache independente de cinco minutos. Falhas preservam a coleta anterior com aviso e permitem nova tentativa após um minuto. A página pausa consultas enquanto está oculta. Não há monitoramento contínuo sem consultas ao servidor. A exportação estática precisa desses endpoints para funcionar com dados reais.

Validação das novas fontes: `python -m unittest discover -s tests -p test_monitoring.py -v` e `node --test tests/monitoring.test.mjs`. Os testes usam fixtures controladas; o RIPE Atlas também foi consultado de verdade. Cloudflare autenticado ainda precisa ser validado com uma credencial válida.

## Licença

Copyright 2026 Pedro Grangeiro e contribuidores. Código, documentação original e dados sintéticos próprios sob **[Apache-2.0](LICENSE)**. Permite reutilização, inclusive comercial, com as obrigações de avisos e atribuição aplicáveis.

**Dados externos têm condições separadas:** IBGE sob CC BY 4.0; dados da API Cloudflare Radar sob CC BY-NC 4.0; dados RIPE Atlas sujeitos a permissão prévia para uso comercial; dados IODA sem concessão aberta de redistribuição identificada. O repositório não distribui caches de observações reais.

Veja [NOTICE](NOTICE), [avisos de terceiros](THIRD_PARTY_NOTICES.md) e [comparação das licenças](docs/research/LICENSE_RESEARCH.md).
