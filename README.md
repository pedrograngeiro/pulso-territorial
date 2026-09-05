# Mapa do Silêncio

MVP local de inteligência territorial para replay e análise de sinais positivos e negativos de enchentes urbanas. A demonstração é inteiramente sintética, agregada por município e não emite alertas nem encaminha pedidos de socorro.

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

O comando executa sete testes (incluindo HTTP ponta a ponta), verifica que não há imports de pacotes externos, gera o relatório comparativo dos quatro detectores, o relatório de licenças e o SBOM SPDX.

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
- [Matriz de licenças](docs/LICENSE_MATRIX.md) e [proposta de licença](LICENSE-PROPOSAL.md)
- [Arquitetura](docs/ARCHITECTURE.md) e [glossário](CONTEXT.md)
- [Privacidade](docs/PRIVACY.md), [modelo de ameaças](docs/THREAT_MODEL.md) e [validação](docs/VALIDATION_PLAN.md)
- [Avisos de terceiros](THIRD_PARTY_NOTICES.md)

## Limitações materiais

Ainda não há validação com dataset histórico, malha IBGE real, persistência PostGIS, feriados/sazonalidade, teste sistemático de perda parcial de fontes, ingestão ao vivo ou detector de bots. Esses itens exigem primeiro validar a licença do recurso concreto e, para dados pessoais, aprovar RIPD/base legal/retensão. As métricas sintéticas não estimam desempenho real.
