# Licença do Pulso Territorial

Consulta: 5 de setembro de 2026 (Brasil). Escopo: código próprio, publicação pública no GitHub e fontes já incorporadas ou consumidas.

## Recomendação

Adotar **Apache-2.0 para código, documentação original e dados sintéticos próprios**. É uma escolha de projeto: favorece reutilização por comunidades, pesquisadores, órgãos públicos e empresas, com regras explícitas sobre patentes e avisos. Não exigir reciprocidade de serviços modificados é um compromisso consciente desta recomendação.

| Licença | Direitos e deveres relevantes | Adequação |
|---|---|---|
| Apache-2.0 | Permite uso comercial e redistribuição; inclui concessão expressa de patentes dos contribuidores, com limites e término em determinadas ações patentárias. Exige conservar licença e avisos aplicáveis, indicar arquivos modificados e preservar atribuições de NOTICE quando existente. Não concede uso geral de marcas. | Recomendada: concessão mais detalhada, sem exigir abertura de todo derivado. |
| MIT | Permite usar, modificar, distribuir, sublicenciar e vender; exige conservar o aviso de copyright e a permissão. Não contém uma cláusula expressa de patentes equivalente à Apache. | Boa alternativa se a prioridade absoluta for um texto mínimo. |
| AGPL-3.0 | Copyleft; também permite uso comercial. A seção 13 exige que uma versão modificada ofereça seu código correspondente aos usuários que interagem com ela remotamente pela rede. | Preferível se a prioridade for manter disponíveis as modificações de serviços derivados. Essa intenção não foi expressa pelo usuário. |

Textos primários: [Apache Software Foundation, Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0), [MIT publicada pela OSI](https://opensource.org/license/mit), [AGPL-3.0 publicada pela OSI, texto da Free Software Foundation](https://opensource.org/license/agpl-3.0). Os endereços GNU falharam nesta consulta; a versão integral publicada pela OSI foi consultada. Não confundir AGPL com licença que proíbe comércio.

Aplicação recomendada: arquivo LICENSE com o texto integral inalterado, identificação do titular real, aviso de escopo no README e THIRD_PARTY_NOTICES.md. Um NOTICE pode registrar as atribuições pertinentes. A ASF recomenda incluir LICENSE e considerar NOTICE; não é necessário transferir a titularidade à ASF. [Orientação oficial](https://www.apache.org/foundation/license-faq.html#Apply-My-Software).

## GeoJSON IBGE

Os arquivos inspecionados são:

- `src/mapa_silencio/static/rio-state.geojson`: contorno de código 33; propriedades originais `codarea`.
- `src/mapa_silencio/static/rio-municipalities.geojson`: 92 municípios, com nomes, identificadores e centros calculados acrescentados pelo projeto; coleta registrada em 05/09/2026.

Proveniência: [estado 33, qualidade mínima](https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo%2Bjson&qualidade=minima), [subdivisão municipal](https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao=municipio), [nomes municipais](https://servicodados.ibge.gov.br/api/v1/localidades/estados/33/municipios), [documentação da API v3](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3).

As notas metodológicas 01/2024 do IBGE abrangem polígonos municipais e agregações estaduais (página impressa 5) e disponibilizam MMD e derivados sob licença compatível com CC BY 4.0 (página 8). Permitem redistribuição e adaptação, inclusive comercial, com crédito. O documento orienta acompanhar os arquivos com sua íntegra e informa que substitui notas anteriores, preservadas especificidades técnicas. [Publicação integral do IBGE](https://biblioteca.ibge.gov.br/visualizacao/livros/liv102152.pdf).

**Não foi identificado impedimento à redistribuição destes limites com atribuição.** Aplicar essa concessão às malhas simplificadas da API é uma inferência fundamentada em sua origem e natureza derivada; o ano específico da geometria não consta nos metadados locais nem foi estabelecido pela documentação consultada. Não apresentar a coleta de 2026 como edição cartográfica 2026. Preservar essa limitação e disponibilizar a íntegra das notas junto aos arquivos.

Registrar IBGE como fonte, URLs, coleta, qualidade mínima, licença e modificações locais. Manter os limites sob CC BY 4.0, separados do código Apache. O crédito deve incluir indicação de alterações, referência à licença e não sugerir endosso do IBGE. [Condições CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Dados consultados em execução

| Fonte | Condição encontrada | Consequência para o repositório |
|---|---|---|
| IODA / Georgia Tech | A consulta pública devolveu aviso de copyright 2021–2025 da Georgia Tech Research Corporation, com reserva de direitos. Não foi localizada concessão aberta de redistribuição dos dados nesta consulta. | Publicar o consumidor independente; conservar o copyright retornado e não versionar snapshots reais nem atribuir Apache aos dados. |
| RIPE Atlas / RIPE NCC | Termos v3.4, art. 4.5: pesquisa e uso responsável; uso comercial dos dados exige permissão prévia da RIPE NCC. Art. 10.3 estabelece condição de autorização para reprodução da propriedade intelectual da RIPE NCC. | Código consumidor independente pode ser Apache. Preservar atribuição e não anunciar os dados como livres para todo uso comercial; não publicar catálogo bruto de sondas ou cache no Git. |
| Cloudflare Radar | Dados dos endpoints da API são CC BY-NC 4.0. A página About distingue imagens e gráficos incorporáveis CC BY 4.0 dos dados da API. | Código pode ser Apache; dados continuam com atribuição e restrição não comercial. Não prometer um serviço comercial autorizado apenas porque o código é aberto. |

Fontes: [API IODA](https://api.ioda.inetintel.cc.gatech.edu/v2/), [consulta IODA reproduzível](https://api.ioda.inetintel.cc.gatech.edu/v2/entities/query?entityType=region&relatedTo=country/BR&search=Rio%20de%20Janeiro&limit=10), [termos RIPE Atlas v3.4, artigos 4 e 10](https://atlas.ripe.net/assets/legal/RIPEAtlasServiceTermsandConditionsV3.4.pdf), [documentação Cloudflare Radar](https://developers.cloudflare.com/radar/), [Radar About](https://radar.cloudflare.com/about), [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

A ausência de chave na API não é licença de redistribuição. Publicar consumidores escritos pelo projeto não transfere os direitos dos dados consumidos. O escopo desta decisão é o repositório de software; uma futura hospedagem de resultados reais ou exploração comercial deve observar os termos específicos acima.

OpenStreetMap permanece separado: dados sob ODbL e tiles sujeitos à política do serviço, com atribuição visível. Carregar tiles no navegador não os torna arquivos Apache do projeto. [Copyright OSM](https://www.openstreetmap.org/copyright), [política de tiles](https://operations.osmfoundation.org/policies/tiles/).

## Publicação

Manter no Git apenas fontes, testes, documentação, dados sintéticos e assets com proveniência registrada; excluir tokens, arquivos de ambiente privados e caches reais. Corrigir notas antigas que ainda tratam a licença própria como pendente ou atribuem uma única licença a todos os dados.

O nome Pulso Territorial descreve a observação de conectividade e comporta expansão geográfica. Esta pesquisa não constitui busca de disponibilidade de marca e não determina exclusividade sobre o nome.
