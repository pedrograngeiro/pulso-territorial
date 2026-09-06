# Avisos de terceiros

## Runtime

O projeto requer CPython 3.13.7, distribuído separadamente sob a PSF License (`Python-2.0`). O código e a biblioteca padrão do Python não são copiados para este repositório. Consulte <https://docs.python.org/3/license.html>.

O frontend usa recursos nativos do navegador (ECMAScript, SVG e CSS), sem bibliotecas JavaScript externas. Os ícones funcionais são SVGs do projeto.

A interface carrega DM Sans e Space Grotesk pelo Google Fonts (SIL Open Font License). Há fallback para fontes do sistema. Os arquivos das fontes não são incorporados ao repositório.

O mapa-base carrega tiles públicos de `tile.openstreetmap.org` sob a política de uso do serviço: <https://operations.osmfoundation.org/policies/tiles/>. A atribuição permanece visível no mapa. Os dados do OpenStreetMap têm licença ODbL; consulte <https://www.openstreetmap.org/copyright>. Os tiles são requisitados somente para a área visível e não são distribuídos no repositório.

## Dados e assets

O cenário, os pontos aproximados e as métricas da demonstração foram criados para este projeto. Eles não são dados oficiais do IBGE, OpenStreetMap, redes sociais ou sensores e não devem ser usados para navegação ou resposta operacional. A cartografia de fundo do OpenStreetMap é independente das observações sintéticas sobrepostas. Os círculos não representam áreas de impacto; as conexões representam somente a ordem de detecção do silêncio.

O repositório contém links/citações a documentos oficiais para pesquisa. Links e fatos citados não significam que datasets ou conteúdo dessas fontes tenham sido incorporados.

## Licença do projeto

A licença do código e dos dados sintéticos ainda depende de aprovação; veja `LICENSE-PROPOSAL.md` e o ADR proposto. Não interpretar esta nota como concessão de licença.

## Contorno estadual do Rio de Janeiro

A malha simplificada do estado (código 33) foi obtida da API de Malhas do IBGE em 2026-09-05 e incorporada em src/mapa_silencio/static/rio-state.geojson. Fonte: <https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo%2Bjson&qualidade=minima>. Documentação: <https://servicodados.ibge.gov.br/api/docs/malhas?versao=3>. O IBGE é creditado na interface. Essa geometria é cartografia de referência, independente dos sinais simulados.

## Monitoramento local

A malha dos 92 municípios fluminenses foi obtida do [IBGE](https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao=municipio), qualidade mínima, em 2026-09-05. Nomes: [API de Localidades](https://servicodados.ibge.gov.br/api/v1/localidades/estados/33/municipios). O arquivo `rio-municipalities.geojson` adiciona nomes, códigos e centros cartográficos calculados à geometria oficial. Não serve para localizar endereços com precisão.

A tela local consulta RIPE Atlas / RIPE NCC e, quando configurado, Cloudflare Radar. Os consumidores são implementações independentes; não incorporam código desses serviços. Fontes e links são exibidos na interface. Dados de sondas são normalizados sem expor seus IPs ou coordenadas. Relatos do Radar são atribuídos e vinculados à origem. Dados externos não herdam a licença proposta do projeto.
