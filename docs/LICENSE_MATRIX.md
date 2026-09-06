# Licenças e condições de uso

Consulta: 05/09/2026. O código próprio do **Pulso Territorial** adota Apache-2.0. [Pesquisa primária](research/LICENSE_RESEARCH.md) e [licença](../LICENSE).

| Material | Instrumento | Distribuição |
|---|---|---|
| Código, documentação original, fixtures sintéticas | Apache-2.0 | Incluídos; preservar licença e avisos aplicáveis |
| Geometrias IBGE e notas técnicas | Compatível com CC BY 4.0 | Incluídas com fonte, alterações e nota integral |
| Dados IODA | Copyright reservado; licença aberta não identificada | Não incluídos; consumidor independente |
| Dados RIPE Atlas | Termos RIPE NCC; uso comercial exige permissão prévia | Não incluídos; consumidor independente |
| Dados da API Cloudflare Radar | CC BY-NC 4.0 | Não incluídos; consumidor exige token |
| Dados OpenStreetMap | ODbL; política separada dos tiles | Tiles consultados em execução |
| DM Sans e Space Grotesk | SIL OFL; serviço Google Fonts | Consultadas em execução |
| CPython e biblioteca padrão | Python-2.0 | Runtime fornecido separadamente |
| Navegador e APIs nativas | Plataforma do usuário | Não distribuídos |

Não há dependências PyPI/npm. O SBOM identifica projeto, runtime e cartografia incorporada. Novos pacotes e datasets precisam de licença e origem documentadas.

Permissão comercial do código não autoriza automaticamente uso comercial dos dados consumidos. Consulta pública, token, licença de dados e atribuição são requisitos distintos. [Atribuições detalhadas](../THIRD_PARTY_NOTICES.md).

A verificação local executa testes Python, verifica imports e gera relatórios e SBOM; não substitui auditoria jurídica ou scanner completo de vulnerabilidades.
