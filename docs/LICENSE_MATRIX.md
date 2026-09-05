# Matriz de licenças e instrumentos

**Consulta:** 30 de agosto de 2026. Esta matriz é triagem técnica, não aconselhamento jurídico. A licença definitiva do projeto está pendente de aprovação humana.

## Instrumentos que não devem ser confundidos

| Instrumento | Cobre | Não resolve |
|---|---|---|
| Licença de software | Código fonte/binário | Direitos sobre posts, bases e pesos |
| Licença de banco de dados | Seleção/estrutura e direitos da base | Contrato de API ou dados pessoais |
| Termos contratuais de API | Acesso, finalidade, cache, display, retenção, término | Licença geral do conteúdo |
| Política de tiles | Capacidade, cache, identificação e volume do servidor | Licença do dado cartográfico |
| Direitos de conteúdo de usuário | Obra/post do autor | Base legal LGPD |
| Proteção de dados pessoais | Todo tratamento de dado pessoal | Copyright/licença comercial |
| Licença de modelo/pesos/dataset | Cada artefato separadamente | Os outros dois artefatos |

## Software efetivamente executado pelo projeto

| Item | Versão | Finalidade | SPDX | Relação | Compatibilidade preliminar |
|---|---:|---|---|---|---|
| Mapa do Silêncio | 0.1.0 | Aplicação | `NOASSERTION` | Projeto | Decisão pendente |
| CPython | 3.13.7 | Runtime externo | `Python-2.0` | Ambiente | Compatível com Apache-2.0 ou AGPL-3.0 |
| Biblioteca padrão Python | 3.13.7 | HTTP, JSON, estatística e testes | `Python-2.0` | Parte do runtime | Compatível |
| Navegador/ECMAScript/SVG/CSS | Fornecido pelo usuário | Interface | N/A, plataforma não distribuída | Ambiente | Não é dependência empacotada |

Não há dependências PyPI, npm, fontes web, ícones, tiles, modelos, pesos ou datasets de terceiros no runtime. Portanto, não há dependências transitivas de pacote no MVP. O contorno do Brasil e os dados são esquemáticos e criados no projeto; não são malha IBGE ou dado OSM.

## Dados candidatos

| Dado/serviço | Licença ou contrato | Comercial | Redistribuição/transformação | Decisão |
|---|---|---|---|---|
| Sintético do projeto | Pendente junto da licença do projeto | Pendente | Pendente | Aprovado internamente |
| IBGE Malha Municipal Digital | CC BY 4.0 na nota oficial; conferir edição | Sim | Sim, com atribuição e alterações | Aprovada |
| OSM data | ODbL 1.0 | Sim | Share-alike/atribuição aplicáveis | Restrita |
| OSM public tiles | Política operacional separada | Não presumir CDN | Cache/bulk limitados | Rejeitada no MVP |
| ANEEL interrupções | ODbL no catálogo | Sim | Obrigações de base derivada/produzida | Restrita |
| ONS conjuntos marcados | CC BY, versão por item | Sim | Sim, atribuição/alterações | Restrita |
| ANA catalogado aberto | Declaração federal de dados abertos; conferir item | Em princípio | Conferir metadado concreto | Restrita |
| INPE catalogado aberto | Declaração de dados abertos; conferir coleção/parceiros | Por item | Por item | Restrita |
| X | Contrato Developer, não licença aberta | Por plano/caso aprovado | Fortemente limitada; exclusões sincronizadas | Experimental/rejeitada na demo |
| Bluesky/Mastodon | Protocolo/software não licencia posts | Não presumir | Minimização e exclusões; termos do host/autor | Experimental |
| INMET, Cemaden, S2iD, Anatel, Defesa Civil | Licença inequívoca não localizada para todo recurso | Não presumir | Somente após conferir export | Experimental/restrita |

## Gate automatizado

`python tools/verify.py` analisa imports do código, falha se encontrar pacote externo não declarado, gera `artifacts/license-report.json`, `artifacts/validation-report.json` e `sbom.spdx.json`, compila o código e executa os testes. Vulnerabilidades do runtime Python e da imagem/SO continuam exigindo scanner externo no ambiente de entrega; não há pacote aplicativo para `pip-audit` ou `npm audit` neste corte.

São bloqueados sem aprovação explícita: GPL/AGPL incorporada como dependência, SSPL, Commons Clause, `source available`, `research only`, `non-commercial`, modelo/peso/dataset sem licença própria e qualquer asset cuja origem não seja rastreável.
