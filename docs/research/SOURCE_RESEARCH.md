# Pesquisa de fontes, acesso e licenças — Mapa do Silêncio

**Data da consulta:** 30 de agosto de 2026  
**Escopo:** fontes candidatas para um MVP brasileiro de detecção retrospectiva de enchentes urbanas.  
**Natureza:** análise técnica preliminar, não aconselhamento jurídico. Antes de produção ou uso comercial, os termos aplicáveis e a base legal de tratamento devem ser validados por responsável jurídico e de privacidade.

## Resumo executivo

O MVP pode ser demonstrado sem API paga e sem conteúdo pessoal real: dados sintéticos reproduzíveis, limites municipais do IBGE e, após registrar a atribuição/licença do conjunto concreto, dados físicos ou históricos de ANA, ANEEL, ONS, INMET, Cemaden e S2iD. OSM é adequado como dado cartográfico sob ODbL, mas o servidor público `tile.openstreetmap.org` não é um serviço gratuito irrestrito para aplicações. Redes sociais devem ser adaptadores opcionais: X exige acesso e caso de uso oficialmente aprovados; Bluesky torna conteúdo acessível pelo protocolo, mas isso não equivale a licenciar conteúdo de usuários; em Mastodon, licença do software e política de cada instância não concedem direitos gerais sobre publicações.

Decisões preliminares:

- **Aprovada:** dado sintético; malhas municipais do IBGE; conjuntos ANA explicitamente catalogados como abertos, sujeitos à conferência do item; dados OSM com atribuição/ODbL e infraestrutura própria ou provedor de tiles compatível.
- **Aprovada com restrições:** ANEEL/ODbL, ONS/CC BY, S2iD/Atlas, Anatel, INPE e arquivos INMET cuja licença/metadados sejam confirmados; uso apenas agregado, com proveniência e atribuição.
- **Experimental:** Bluesky, Mastodon, Cemaden, Defesa Civil Alerta/IDAP e APIs oficiais que exigem solicitação, cadastro ou cujos termos específicos não estavam publicados de forma inequívoca.
- **Rejeitada para a demonstração básica:** X ao vivo, scraping de qualquer plataforma, tiles públicos OSM como backend de produção, dados pessoais brutos e qualquer modelo/dataset sem licença separadamente verificada.

## O que cada instrumento jurídico cobre

Estes instrumentos não são intercambiáveis:

1. **Licença de software** cobre código executável ou fonte. Apache-2.0, MIT ou AGPL do servidor/protocolo não licenciam automaticamente os dados processados por ele.
2. **Licença de banco de dados** cobre a base como coleção e, conforme a jurisdição/licença, seus direitos sui generis; a ODbL pode exigir atribuição, compartilhamento pela mesma licença de bases derivadas e oferta aberta de bases produzidas usadas publicamente.
3. **Contrato/termos de API** define quem pode acessar, para quais casos de uso, limites, retenção, cache, exibição e término. Pode restringir atividades que a licença do software não restringe.
4. **Política de mapas/tiles** regula capacidade operacional, cache, identificação do cliente e volume no servidor que renderiza mapas; é distinta da licença do dado geográfico.
5. **Direitos sobre conteúdo de usuários** permanecem, em regra, com autores ou outros titulares; a publicação pública não é uma licença geral de armazenamento, transformação ou redistribuição.
6. **Proteção de dados pessoais** regula operações de tratamento independentemente de copyright. A LGPD define tratamento de modo amplo e exige finalidade, adequação, necessidade, qualidade, transparência, segurança, prevenção, não discriminação e prestação de contas; mesmo dados tornados públicos devem ser tratados considerando finalidade, boa-fé e interesse público ([Lei 13.709/2018, arts. 5º–7º](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm)). A LGPD não fixa um prazo universal de retenção; ele depende da finalidade e circunstâncias ([ANPD, perguntas frequentes](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes)).
7. **Licença de modelo, pesos e dados de treinamento** são três avaliações independentes. Uma biblioteca permissiva não torna permissivos os pesos nem o corpus; um cartão de modelo também pode não resolver direitos sobre dados de treinamento ou saída.

“Dado aberto” deve ser comprovado no catálogo ou licença do conjunto concreto. A Política de Dados Abertos federal define dado aberto como disponibilizado sob licença aberta que permita livre utilização, consumo ou cruzamento ([Decreto 8.777/2016](https://planalto.gov.br/ccivil_03/_ato2015-2018/2016/decreto/d8777.htm)); isso não autoriza presumir que todo conteúdo visível em um portal seja aberto.

## Critério de decisão

- **Aprovada:** acesso e licença oficiais são claros, compatíveis com o MVP e sem credencial/aceite em nome do responsável.
- **Aprovada com restrições:** utilizável somente com obrigações técnicas, atribuição, share-alike, granularidade, finalidade ou validação item a item.
- **Experimental:** interface ou prova limitada; pendem termos, autorização, estabilidade, base legal ou confirmação do titular.
- **Rejeitada:** conflita com o uso, requer conduta proibida/não autorizada ou apresenta risco desproporcional.

Campos “não localizado” significam apenas que a página oficial consultada não informou a condição; não significam permissão.

## Matriz detalhada

### 1. Dataset sintético do próprio projeto

- **Proprietário/URL:** projeto Mapa do Silêncio; arquivo local a ser gerado e documentado.
- **Acesso permitido:** geração local determinística, sem coleta externa.
- **Licença/direitos:** o projeto pode licenciar os registros que criar, desde que não copie conteúdo, geometrias ou estatísticas protegidas de terceiros. A licença definitiva do projeto depende de aprovação humana.
- **Comercial, armazenar, transformar, redistribuir:** tecnicamente permitidos pelo titular; documentar separadamente licença do código e dos dados.
- **Atribuição, retenção, exclusão:** definidas pelo projeto; não conter autores, mensagens reais nem coordenadas residenciais.
- **Limites/custos:** nenhum serviço externo; apenas recursos locais.
- **Privacidade:** baixa se pessoas e fatos não forem reidentificáveis; rotular em todos os registros e telas como **SIMULADO**.
- **Decisão:** **aprovada** e fonte padrão da demonstração.

### 2. X / Twitter API

- **Proprietário/URL:** X Corp.; [Developer Agreement](https://docs.x.com/developer-terms/agreement), [Developer Policy](https://docs.x.com/developer-terms/policy), [Restricted Uses](https://docs.x.com/developer-terms/restricted-use-cases), [pricing](https://docs.x.com/x-api/getting-started/pricing).
- **Acesso permitido:** somente API e produtos oficialmente autorizados, com conta/projeto e caso de uso declarados; scraping e contorno de autenticação ficam fora do escopo.
- **Licença/termos:** contrato de API, não licença aberta do conteúdo. O desenvolvedor recebe acesso condicionado e deve respeitar políticas de exibição, automação, uso e restrições adicionais do produto.
- **Comercial:** depende do nível contratado, aprovação do caso de uso e termos vigentes; usos além da integração/prototipagem ordinária e casos governamentais podem exigir Enterprise. Não presumir autorização porque a publicação é pública ([Developer Policy](https://docs.x.com/developer-terms/policy)).
- **Armazenar/transformar/redistribuir:** a política admite quantidade razoável para análise aprovada e, em regra, redistribuição de IDs, com limites próprios; conteúdo só pode ser alterado para formatação. Geodados não podem ser separados nem armazenados fora do post, embora heatmaps agregados sejam contemplados. Não armazenar texto integral no MVP sem confirmação contratual específica ([Developer Policy](https://docs.x.com/developer-terms/policy)).
- **Atribuição:** seguir requisitos oficiais de display/branding quando conteúdo for exibido.
- **Retenção/exclusão:** conteúdo removido, protegido, suspenso, alterado ou sem geotag deve ser atualizado/excluído tão logo possível e, quando houver pedido escrito de X ou usuário, em até 24 horas; não foi localizado um prazo máximo geral de retenção ([Developer Policy](https://docs.x.com/developer-terms/policy)).
- **Limites/custos:** o modelo consultado é *pay-per-use* e a página publicava US$ 0,005 por leitura de post e teto comum de 2 milhões de leituras mensais, com Enterprise acima disso; preço é mutável e o console é a referência final ([pricing consultado em 2026-08-30](https://docs.x.com/x-api/getting-started/pricing)). Não foi criada conta nem aceito contrato nesta pesquisa.
- **Privacidade/risco:** texto, identificadores, perfil e localização podem ser dados pessoais. As regras proíbem usos contrários à expectativa razoável de privacidade, certos perfis sensíveis, vigilância/inteligência e monitoramento de eventos sensíveis; análise agregada sem identificadores pode ser aceita, mas é incerto se este produto seria classificado como inteligência/surveillance ([Restricted Uses](https://docs.x.com/developer-terms/restricted-use-cases)). Exige aprovação escrita do caso de uso, LGPD, agregação e proibição de perfis individuais.
- **Decisão:** **experimental somente após aprovação escrita do caso de uso e validação jurídica/contratual; rejeitada como dependência do MVP**. Entregar apenas interface e fixture agregada.

### 3. Bluesky / AT Protocol

- **Proprietário/URL:** Bluesky Social PBC e rede AT Protocol; [Developer Guidelines](https://bsky.network/docs/developer-guidelines/), [Jetstream replay](https://bsky.network/docs/jetstream-replay/), [rate limits](https://bsky.network/docs/rate-limits/), [Bluesky Terms of Service](https://bsky.social/about/support/tos).
- **Acesso permitido:** endpoints públicos e stream do protocolo conforme documentação, respeitando limites, autenticação e termos do serviço/host usado.
- **Licença/termos:** código e especificações do protocolo não concedem licença geral sobre posts. Os termos do serviço e direitos do autor continuam aplicáveis ao conteúdo.
- **Comercial:** não presumido para reutilização de conteúdo; validar finalidade, host e termos antes de produto comercial.
- **Armazenar/transformar/redistribuir:** o fato de registros serem recuperáveis no repositório/firehose não resolve copyright, LGPD, exclusões ou redistribuição. Para experimento, guardar apenas IDs, buckets agregados e atributos derivados minimizados, com prazo curto.
- **Atribuição:** se houver exibição, preservar autoria/contexto segundo termos e design oficial; o MVP não exibirá posts brutos.
- **Retenção/exclusão:** as diretrizes exigem meio de excluir conteúdo a pedido; Jetstream entrega eventos de criação/atualização/exclusão e exclusão de conta. Consumir esses eventos e remover derivados vinculáveis; prazo máximo contratual não foi localizado ([Developer Guidelines](https://bsky.network/docs/developer-guidelines/), [Jetstream](https://bsky.network/docs/jetstream-replay/)).
- **Limites/custos:** a documentação consultada publicava, para o PDS da Bluesky, 3.000 requisições por 5 minutos por IP; limites variam por serviço/host, e replay pode responder `429` ([rate limits](https://bsky.network/docs/rate-limits/)). Operar firehose completo não é necessário para o MVP.
- **Privacidade/risco:** identificadores descentralizados, texto, grafo social e localização textual permitem reidentificação; instâncias/PDS podem ter políticas distintas.
- **Decisão:** **experimental**; adaptador desabilitado, sem dados reais na demo, até DPIA/RIPD, termos e política de retenção aprovados.

### 4. Mastodon / Fediverse

- **Proprietário/URL:** Mastodon gGmbH mantém o software; cada servidor/instância controla seu serviço e seus termos. [dados públicos](https://docs.joinmastodon.org/client/public/), [timelines](https://docs.joinmastodon.org/methods/timelines/), [API de instância/termos/privacidade](https://docs.joinmastodon.org/methods/instance/), [limites](https://docs.joinmastodon.org/api/rate-limits/), [repositório/licença do software](https://github.com/mastodon/mastodon).
- **Acesso permitido:** API documentada de uma instância, conforme sua configuração, autenticação, robots e termos. Não existe autorização global para todas as instâncias.
- **Licença/termos:** AGPL-3.0 do software Mastodon cobre o código do servidor, não os posts; políticas e direitos de conteúdo variam por instância e autor.
- **Comercial:** deve ser validado instância a instância; licença AGPL do software não autoriza monetizar/republicar conteúdo de usuário.
- **Armazenar/transformar/redistribuir:** somente o mínimo permitido pela instância e pela lei; preferir contagens agregadas. Conteúdo federado pode ter origem em outro servidor, aumentando a cadeia de direitos e exclusão.
- **Atribuição:** conforme termos da instância e direitos do autor; não exibir mensagens brutas no MVP.
- **Retenção/exclusão:** observar exclusões federadas e estabelecer TTL curto; não foi localizada regra universal porque não há controlador contratual único.
- **Limites/custos:** o padrão documentado do software é 300 requisições por 5 minutos por conta e por IP, mas administradores podem alterar limites e bloquear clientes; custo/SLA é do operador/instância ([Mastodon API](https://docs.joinmastodon.org/api/rate-limits/)).
- **Privacidade/risco:** visibilidade “pública” no protocolo não elimina expectativa contextual, LGPD nem risco de localizar pessoas vulneráveis.
- **Decisão:** **experimental**, lista explícita de instâncias aprovadas e sem coleta no MVP inicial.

### 5. INMET — estações, histórico e alertas meteorológicos

- **Proprietário/URL:** Instituto Nacional de Meteorologia/Ministério da Agricultura e Pecuária; [portal e serviços](https://www.gov.br/agricultura/pt-br/assuntos/inmet/capa), [acesso a dados](https://portal.inmet.gov.br/noticias/saiba-como-acessar-os-dados-meteorol%C3%B3gicos-dispon%C3%ADveis-no-site-do-inmet), [contato oficial da API](https://portal.inmet.gov.br/fale-conosco), [plano/produtos](https://portal.inmet.gov.br/uploads/notastecnicas/V.5_Planejamento_Estrategico_INMET.pdf).
- **Acesso permitido:** dados observados, históricos anuais e BDMEP são oferecidos ao público; acesso à API deve ser solicitado pelo canal oficial `api@inmet.gov.br`. O INMET declara históricos horários desde 2000 e público-alvo incluindo instituições públicas, privadas, pesquisadores e público geral ([documento de produtos, pp. 33–34](https://portal.inmet.gov.br/uploads/notastecnicas/V.5_Planejamento_Estrategico_INMET.pdf)).
- **Licença/termos:** o portal de dados abertos do MAPA descreve dados abertos como livremente utilizáveis e redistribuíveis ([MAPA](https://www.gov.br/agricultura/pt-br/acesso-a-informacao/dadosabertos/dados-abertos-disponibilizados)), mas não foi localizada na consulta uma licença inequívoca anexada a cada arquivo INMET/API. A licença CC BY-ND do texto do site não deve ser aplicada automaticamente à base.
- **Comercial:** **não confirmado para o arquivo/API específico**; público-alvo privado não equivale a licença comercial.
- **Armazenar/transformar/redistribuir:** apenas depois de registrar a licença/metadado do recurso ou obter confirmação oficial; transformação é incompatível com uma leitura literal de BY-ND caso essa fosse a licença do dado, por isso não inferir.
- **Atribuição:** creditar INMET/MAPA, estação, instante, versão/data de download e URL.
- **Retenção/exclusão:** não localizada regra específica para observações meteorológicas; manter proveniência e política interna, sem supor retenção ilimitada da API.
- **Limites/custos:** API requer solicitação; preço/cota não publicados na página de contato consultada. Arquivos históricos são alternativa sem credencial paga.
- **Privacidade:** observações de estações têm baixo risco; dados de conta/solicitação são pessoais. Alertas não devem ser representados como garantia de segurança.
- **Decisão:** **aprovada com restrições para arquivos cuja licença seja confirmada; API experimental**. Para demo, fixture sintética ou arquivo baixado manualmente com metadados.

### 6. Cemaden — pluviômetros, hidrologia, radares e alertas

- **Proprietário/URL:** Centro Nacional de Monitoramento e Alertas de Desastres Naturais/MCTI; [Mapa Interativo](https://mapainterativo.cemaden.gov.br/), [FAQ oficial](https://www.gov.br/cemaden/pt-br/paginas/historico-da-criacao-do-cemaden), [manual do mapa](https://mapainterativo.cemaden.gov.br/arquivos/MapaInterativo.pdf), [acesso à informação](https://www.gov.br/cemaden/pt-br/acesso-a-informacao).
- **Acesso permitido:** visualização quase em tempo real; download histórico mensal de pluviômetros desde 2013 e download de radar pelo mapa. O fluxo histórico pode pedir nome/e-mail e captcha; dados hidrológicos são enviados por link de e-mail ([FAQ](https://www.gov.br/cemaden/pt-br/paginas/historico-da-criacao-do-cemaden), [manual, seção 2.7](https://mapainterativo.cemaden.gov.br/arquivos/MapaInterativo.pdf)). Os registros usam UTC ([Mapa Interativo](https://mapainterativo.cemaden.gov.br/)).
- **Licença/termos:** não foi localizada licença explícita por conjunto nem termo autorizando automação/redistribuição. A cultura institucional de dados abertos não substitui uma licença do recurso.
- **Comercial, armazenamento, transformação e redistribuição:** **não confirmados**; não automatizar captcha/formulário nem simular consentimento.
- **Atribuição:** se autorizado, creditar Cemaden/MCTI, estação/radar, instante e data de obtenção.
- **Retenção/exclusão:** não localizada regra pública específica; e-mail de solicitante deve ser minimizado e não entrar no dataset.
- **Limites/custos:** histórico é baixado mês a mês; não há custo indicado, mas há barreira operacional/formulário. Sem API pública confirmada.
- **Privacidade:** sensores físicos têm risco baixo; alertas/ocorrências podem revelar áreas vulneráveis, e dados fornecidos no formulário são pessoais.
- **Decisão:** **experimental** até confirmação escrita da licença e método de automação. Pode ser referência externa/manual de validação, não ingestão automática no MVP.

### 7. INPE/CPTEC — meteorologia, satélite e produtos ambientais

- **Proprietário/URL:** Instituto Nacional de Pesquisas Espaciais/MCTI; [Dados Abertos](https://www.gov.br/inpe/pt-br/acesso-a-informacao/dados-abertos/dados-abertos), [serviços](https://www.gov.br/inpe/pt-br/servicos), [portal de dados geoespaciais](https://data.inpe.br/).
- **Acesso permitido:** o INPE oferece conjuntos por categorias e acesso gratuito a dados/produtos de satélites, radares e instrumentos meteorológicos; o portal afirma que dados abertos são livres de restrições de licenças, patentes ou controle ([Dados Abertos](https://www.gov.br/inpe/pt-br/acesso-a-informacao/dados-abertos/dados-abertos)).
- **Licença/termos:** a declaração geral apoia reutilização, mas cada coleção/produto pode incorporar dados de parceiros. Conferir licença, metadados e política do item; “CPTEC/INPE” não é uma licença única.
- **Comercial, armazenamento, transformação e redistribuição:** aprováveis apenas para item catalogado como aberto e sem restrição de terceiro; registrar versão e condições.
- **Atribuição:** INPE/CPTEC e produto/coleção, data, URL e quaisquer créditos adicionais do metadado.
- **Retenção/exclusão:** não localizada regra geral; preservar revisões e substituir produtos corrigidos quando a fonte sinalizar atualização.
- **Limites/custos:** acesso público/gratuito segundo o serviço, mas limites e SLA não foram localizados; não tratar endpoint público como infraestrutura garantida.
- **Privacidade:** baixo para grade meteorológica; imagens de alta resolução e camadas socioambientais exigem avaliação de reidentificação/áreas sensíveis.
- **Decisão:** **aprovada com restrições por coleção**; preferir download versionado a dependência ao vivo.

### 8. ANA — HidroWeb e telemetria hidrológica

- **Proprietário/URL:** Agência Nacional de Águas e Saneamento Básico; [Dados Abertos](https://www.gov.br/ana/pt-br/acesso-a-informacao/dados-abertos), [HidroWeb](https://www.snirh.gov.br/hidroweb/), [solicitação da API](https://www.snirh.gov.br/hidroweb/acesso-api), [manuais das APIs](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais-de-sistemas-e-servicos-de-disponibilizacao-de-dados-hidrologicos).
- **Acesso permitido:** portal público para chuva, nível, vazão, climatologia, qualidade da água e sedimentos; acesso automatizado ao HidroWebservice requer solicitação por e-mail, identificação e avaliação da ANA ([HidroWeb API](https://www.snirh.gov.br/hidroweb/acesso-api)).
- **Licença/termos:** a ANA declara que seus dados abertos são disponibilizados livremente à sociedade, sem restrição de licenças, patentes ou controles ([ANA Dados Abertos](https://www.gov.br/ana/pt-br/acesso-a-informacao/dados-abertos)). Confirmar que o recurso HidroWeb escolhido integra formalmente o catálogo aberto e guardar seu metadado.
- **Comercial, armazenamento, transformação e redistribuição:** tecnicamente compatíveis com a declaração de dados abertos para conjuntos catalogados; não inclui dados pessoais de contas/contatos ou recursos de terceiros fora do catálogo.
- **Atribuição:** ANA/SNIRH/Rede Hidrometeorológica Nacional, estação, data, versão/download e fonte original quando indicada.
- **Retenção/exclusão:** observações físicas não têm prazo localizado; dados cadastrais de usuários do portal são outra categoria e não devem ser ingeridos. A ANA publica política de privacidade do aplicativo HidroWeb ([índice oficial](https://www.gov.br/ana/pt-br/acesso-a-informacao/tecnologia-da-informacao)).
- **Limites/custos:** API requer cadastro e avaliação; cota/custo não informados na página consultada. Downloads manuais autorizados evitam credencial no MVP.
- **Privacidade:** baixo nos sensores; estações e metadados podem conter contato/cadastro, que deve ser excluído do pipeline.
- **Decisão:** **aprovada com restrições para downloads abertos; API experimental até autorização**, sem aceitar termos em nome do usuário.

### 9. Defesa Civil Nacional — S2iD e Atlas Digital de Desastres

- **Proprietário/URL:** Secretaria Nacional de Proteção e Defesa Civil/MIDR; [S2iD](https://www.gov.br/mdr/pt-br/assuntos/protecao-e-defesa-civil/sistema-integrado-de-informacoes-sobre-desastres), [Dados Abertos MIDR](https://www.gov.br/mdr/pt-br/acesso-a-informacao/dados-abertos), [Atlas Digital](https://www.gov.br/mdr/pt-br/noticias/atlas-digital-de-desastres-no-brasil-e-atualizado-com-dados-consolidados-de-2024/).
- **Acesso permitido:** consulta pública de ocorrências/processos no S2iD e Atlas gratuito, sem cadastro, com consolidação anual baseada em registros municipais; o Atlas cobre 1991–2024 na atualização consultada ([MIDR](https://www.gov.br/mdr/pt-br/noticias/atlas-digital-de-desastres-no-brasil-e-atualizado-com-dados-consolidados-de-2024/)).
- **Licença/termos:** o PDA lista “S2ID — Dados Informados” como base aberta; a página institucional está sob CC BY-ND 3.0, mas essa licença do conteúdo da página não deve ser automaticamente atribuída às tabelas/exports ([Dados Abertos MIDR](https://www.gov.br/mdr/pt-br/acesso-a-informacao/dados-abertos)). Conferir o metadado do arquivo exportado.
- **Comercial, armazenamento, transformação e redistribuição:** pendem da licença específica do recurso; análise interna/agregada é preferível, sem republicar formulários ou anexos.
- **Atribuição:** MIDR/SEDEC/S2iD, município declarante, período de consolidação e data de acesso.
- **Retenção/exclusão:** dados consolidados históricos podem ser revisados; atualizar snapshots e registrar versão. Não ingerir campos pessoais, documentos ou contatos.
- **Limites/custos:** Atlas é aberto/gratuito; API pública e limites não foram localizados. Usar export oficial, não scraping de dashboard.
- **Privacidade:** relatos e danos humanos em granularidade fina podem reidentificar vítimas; agregar por município e suprimir células pequenas.
- **Decisão:** **aprovada com restrições para validação histórica**, após conferir a licença do export; não é ground truth instantâneo, pois depende de registro e consolidação municipal.

### 10. Defesa Civil Alerta / IDAP

- **Proprietário/URL:** MIDR/Cenad, com suporte regulatório da Anatel; [Alertas de Desastres](https://www.gov.br/anatel/pt-br/dados/utilidade-publica/alertas-de-desastres), [Defesa Civil Alerta](https://www.gov.br/anatel/pt-br/dados/utilidade-publica/alertas-de-desastres/defesa-civil-alerta), [normas MIDR](https://www.gov.br/mdr/pt-br/acesso-a-informacao/legislacao/gm).
- **Acesso permitido:** painéis públicos permitem consultar notificações por canal, tempo, UF/município e, em alguns casos, conteúdo. A emissão/operação no IDAP é restrita a órgãos autorizados; a Portaria MIDR 2.458/2026 rege o uso atual segundo o índice oficial ([MIDR](https://www.gov.br/mdr/pt-br/acesso-a-informacao/legislacao/gm)).
- **Licença/termos:** nenhuma licença de base/API foi localizada no painel. O acesso visual não autoriza scraping nem redistribuição.
- **Comercial, armazenamento, transformação e redistribuição:** **não confirmados**; usar apenas export oficial explicitamente licenciado ou referência manual.
- **Atribuição:** Cenad/MIDR, Defesa Civil emissora, canal, horário e local, se o recurso permitir.
- **Retenção/exclusão:** não localizada política do conjunto; mensagens podem conter instruções urgentes desatualizadas, portanto nunca reapresentá-las como ativas em replay sem rótulo histórico.
- **Limites/custos:** consulta pública gratuita; API pública não localizada. Não solicitar acesso operacional.
- **Privacidade:** conteúdo agregado é baixo risco; texto/local pode revelar população vulnerável. O projeto não emitirá nem retransmitirá alertas.
- **Decisão:** **experimental como referência histórica/manual; rejeitada para emissão ou automação no MVP**.

### 11. ANEEL — interrupções de energia na distribuição

- **Proprietário/URL:** Agência Nacional de Energia Elétrica; [conjunto Interrupções de Energia Elétrica](https://dadosabertos.aneel.gov.br/pt_BR/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao), [metadado/licença](https://dadosabertos.aneel.gov.br/dataset/groups/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao), [dicionário](https://dadosabertos.aneel.gov.br/dataset/ccb25653-f07b-4f28-84c2-62a89d1f5a56/resource/6e5611de-948d-4473-b309-520d7523b762/download/dm-interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao.pdf).
- **Acesso permitido:** download CSV/ZIP/Parquet e API CKAN. A base cobre interrupções desde 2017, atualização mensal, instante até segundos e “conjunto de unidades consumidoras”; exclui áreas sob permissionárias/cooperativas ([catálogo](https://dadosabertos.aneel.gov.br/pt_BR/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao)).
- **Licença/termos:** **Open Data Commons ODbL** no metadado oficial ([ANEEL](https://dadosabertos.aneel.gov.br/dataset/groups/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao)). É licença de banco, não licença de software.
- **Comercial:** ODbL permite uso comercial com suas condições.
- **Armazenar/transformar/redistribuir:** permitido observando atribuição, manutenção aberta de bases derivadas/produzidas quando acionada e oferta sob ODbL; separar resultados analíticos de uma base derivada e submeter o desenho à revisão jurídica.
- **Atribuição:** ANEEL/SFE, título, versão/data e link; incluir aviso ODbL e disponibilizar a base derivada quando exigido.
- **Retenção/exclusão:** sem prazo específico localizado; atualização mensal e correções devem ser sincronizadas por snapshot/versionamento.
- **Limites/custos:** download gratuito; arquivos podem ser grandes (o recurso 2026 consultado tinha 161 MiB) e API CKAN não implica SLA ([recurso 2026](https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao/resource/33a21bd6-4893-42fc-bc05-888154f7511e)).
- **Privacidade:** granularidade é conjunto/alimentador, não consumidor individual, mas nomes de infraestrutura podem ser sensíveis operacionalmente; não publicar topologia detalhada desnecessária.
- **Decisão:** **aprovada com restrições ODbL**; ótima fonte retrospectiva, não indicador municipal em tempo real.

### 12. ONS — carga e operação do Sistema Interligado Nacional

- **Proprietário/URL:** Operador Nacional do Sistema Elétrico; [Portal de Dados Abertos](https://dados.ons.org.br/), [Carga de Energia Verificada/programação](https://dados.ons.org.br/group/7cdc1933-ed06-492e-ab5b-03876bedddcd?groups=programacao-da-operacao&res_format=API&res_format=JSON&tags=Carga&tags=DESSEM).
- **Acesso permitido:** download CSV/XLSX/Parquet/JSON e API CKAN em conjuntos publicados; carga verificada tem periodicidade semi-horária por área de carga, não município ([catálogo ONS](https://dados.ons.org.br/group/7cdc1933-ed06-492e-ab5b-03876bedddcd?groups=programacao-da-operacao&res_format=API&res_format=JSON&tags=Carga&tags=DESSEM)).
- **Licença/termos:** conjuntos consultados de carga estão marcados **Creative Commons Attribution (CC BY)** ([filtro oficial de licença](https://dados.ons.org.br/dataset/?_tags_limit=0&groups=programacao-da-operacao&license_id=cc-by&organization=ons&res_format=JSON&res_format=PDF&tags=DESSEM&tags=Semi-hor%C3%A1rio)). Conferir versão exata da CC BY no metadado do item.
- **Comercial, armazenamento, transformação e redistribuição:** permitidos pela CC BY, com atribuição e indicação de alterações; não estender a licença a conjuntos ONS não marcados.
- **Atribuição:** ONS, conjunto, data/versão, URL, licença e transformações.
- **Retenção/exclusão:** sem prazo localizado; armazenar snapshots e incorporar correções.
- **Limites/custos:** portal/download/API públicos; sem SLA, cota ou preço localizados.
- **Privacidade:** baixo em dados sistêmicos agregados; insuficiente para concluir apagão municipal e sujeito a confundidores operacionais.
- **Decisão:** **aprovada com restrições e apenas como contexto macrorregional**, não como prova de silêncio local.

### 13. Anatel — qualidade e interrupções de telecomunicações

- **Proprietário/URL:** Agência Nacional de Telecomunicações; [Dados Abertos](https://www.gov.br/anatel/pt-br/dados/dados-abertos), [Resultados de qualidade](https://www.gov.br/anatel/pt-br/dados/qualidade/qualidade-dos-servicos/resultados), [Interrupções](https://www.gov.br/anatel/pt-br/dados/qualidade/qualidade-dos-servicos/interrupcoes-de-servicos).
- **Acesso permitido:** bases e planilhas abertas de indicadores por município/operadora/período; a agência define dado aberto como utilizável/cruzável livremente, limitada a obrigação de crédito ([Anatel Dados Abertos](https://www.gov.br/anatel/pt-br/dados/dados-abertos)).
- **Licença/termos:** confirmar a licença no recurso exportado. A licença CC BY-ND 3.0 exibida no rodapé do portal cobre conteúdo do site e não deve ser automaticamente tratada como licença de cada base. O PDA 2025–2027 lista Selos/IQS como dados abertos.
- **Comercial, armazenamento, transformação e redistribuição:** compatíveis para recursos formalmente abertos, com crédito; transformação pendente se o item estiver apenas sob BY-ND.
- **Atribuição:** Anatel, indicador, operadora quando aplicável, período, versão e URL.
- **Retenção/exclusão:** sem prazo localizado; séries podem ser metodologicamente descontinuadas. A fiscalização municipal anterior cobre 2012–2022 e foi encerrada ([histórico](https://www.gov.br/anatel/pt-br/dados/qualidade/qualidade-dos-servicos/fiscalizacao-municipal-da-telefonia-movel)).
- **Limites/custos:** painéis/planilhas gratuitos; API pública específica e SLA não localizados.
- **Privacidade:** indicadores agregados são baixo risco; medidas intramunicipais/antenas podem expor infraestrutura e não devem ser associadas a usuários. Uma interrupção regulatória é paralisação contínua de pelo menos 10 minutos e, no móvel, afeta mais de 20% das antenas municipais ([Anatel](https://www.gov.br/anatel/pt-br/dados/qualidade/qualidade-dos-servicos/interrupcoes-de-servicos)); não equivale automaticamente à ausência de internet percebida.
- **Decisão:** **aprovada com restrições para baseline/contexto histórico; inadequada como feed de outage em tempo real sem acordo específico**.

### 14. OpenStreetMap — dados geográficos

- **Proprietário/URL:** contribuidores OpenStreetMap, administrados pela OpenStreetMap Foundation; [copyright/licença](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), [diretrizes de atribuição](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines).
- **Acesso permitido:** planet extracts, APIs e provedores autorizados conforme políticas; para processamento municipal, preferir extrato versionado e não consultas massivas ao endpoint principal.
- **Licença/termos:** base sob ODbL 1.0. Estilos, software e tiles podem ter licenças/políticas diferentes.
- **Comercial:** permitido pela ODbL com atribuição e share-alike aplicável.
- **Armazenar/transformar/redistribuir:** permitido sob ODbL; uma base derivada distribuída/publicamente usada pode exigir mesma licença e acesso à base. “Produced Works” têm obrigações de atribuição e aviso.
- **Atribuição:** `© OpenStreetMap contributors`, link para copyright/ODbL e apresentação legível conforme as diretrizes.
- **Retenção/exclusão:** não há prazo geral na ODbL; snapshots ficam desatualizados, e edições/redações devem ser tratadas ao atualizar.
- **Limites/custos:** dados são abertos, mas infraestrutura não é ilimitada; ver tiles abaixo.
- **Privacidade:** objetos OSM podem conter nomes/contatos e mapeamento sensível; filtrar tags pessoais e não enriquecer perfis.
- **Decisão:** **aprovada com restrições ODbL**, útil para vias/rios/POIs, não necessária para a malha municipal oficial.

### 15. Servidor público de tiles do OpenStreetMap

- **Proprietário/URL:** OpenStreetMap Foundation; [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/).
- **Acesso permitido:** uso moderado e interativo que respeite atribuição, identificação/referer, cache e padrões técnicos. Bulk download, prefetch e uso que prejudique o serviço são proibidos pela política.
- **Licença/termos:** política operacional do serviço, separada da ODbL do dado. Não há SLA; acesso pode ser bloqueado sem aviso.
- **Comercial:** a política não transforma o servidor comunitário em CDN de produção; aplicações comerciais/alto volume devem usar provedor ou hospedar tiles.
- **Armazenar/transformar/redistribuir:** cache somente conforme política e cabeçalhos; não montar pacote offline a partir do servidor público.
- **Atribuição:** atribuição OSM visível no mapa.
- **Retenção/exclusão:** cache conforme cabeçalhos/política.
- **Limites/custos:** gratuito e financiado por doações, capacidade limitada, sem garantia.
- **Privacidade:** requisições de tiles revelam IP e viewport ao operador; proxy/provedor próprio pode reduzir exposição, sujeito à sua política.
- **Decisão:** **aprovada apenas para desenvolvimento local leve; rejeitada como infraestrutura de produção/demo de carga**. Preferir basemap vetorial local simplificado ou provedor com contrato compatível.

### 16. IBGE — malhas municipais e códigos territoriais

- **Proprietário/URL:** Fundação Instituto Brasileiro de Geografia e Estatística; [Malhas territoriais](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html), [nota técnica/legal da Malha Municipal Digital](https://www.ibge.gov.br/biblioteca/visualizacao/livros/liv102152.pdf).
- **Acesso permitido:** downloads públicos de malhas em formatos geoespaciais e tabelas/códigos oficiais; selecionar explicitamente o ano de referência e escala.
- **Licença/termos:** a nota oficial declara licença compatível com **CC BY 4.0** para a Malha Municipal Digital; confirmar edição e aviso anexado ao download escolhido ([IBGE, nota técnica/legal](https://www.ibge.gov.br/biblioteca/visualizacao/livros/liv102152.pdf)).
- **Comercial, armazenamento, transformação e redistribuição:** CC BY 4.0 permite compartilhamento e adaptação, inclusive comercial, com atribuição; não apresentar uma simplificação/processamento como geometria oficial inalterada.
- **Atribuição:** `Fonte: IBGE`, produto, ano/escala, URL e descrição das transformações.
- **Retenção/exclusão:** sem prazo localizado; manter versões porque limites e códigos mudam.
- **Limites/custos:** download gratuito; sem SLA para usar o servidor como backend.
- **Privacidade:** malha municipal não contém pessoas; cruzamentos com sinais raros podem reidentificar, exigindo limiares de publicação. A escala indicada na nota é 1:250.000 e não deve ser tratada como levantamento cadastral/exato ([IBGE](https://www.ibge.gov.br/biblioteca/visualizacao/livros/liv102152.pdf)).
- **Decisão:** **aprovada**, fonte canônica de municípios no MVP.

## Fontes históricas recomendadas para validação

### Caso principal: enchentes do Rio Grande do Sul, abril–maio de 2024

Usar uma janela retrospectiva e cruzar fontes independentes, sem declarar nenhuma como verdade perfeita:

- **S2iD/Atlas Digital:** municípios e impactos declarados/consolidados; o Atlas é aberto, gratuito e baseado em registros municipais ([MIDR](https://www.gov.br/mdr/pt-br/noticias/atlas-digital-de-desastres-no-brasil-e-atualizado-com-dados-consolidados-de-2024/)). Adequado para área afetada, mas atrasado e sujeito a diferenças de capacidade administrativa.
- **ANA/HidroWeb:** chuva, nível e vazão em estações ([ANA](https://www.gov.br/ana/pt-br/assuntos/noticias-e-eventos/noticias/hidroweb-esta-disponivel-para-usuarios-as)). Adequado para cronologia física; cobertura espacial desigual e falhas de sensor não são ausência de evento.
- **INMET/Cemaden:** precipitação horária e estações/pluviômetros; Cemaden oferece histórico desde 2013, mês a mês ([Cemaden FAQ](https://www.gov.br/cemaden/pt-br/paginas/historico-da-criacao-do-cemaden)). Só integrar após registrar licença do arquivo.
- **ANEEL:** interrupções horárias por conjunto de unidades consumidoras desde 2017, mensalmente atualizadas ([ANEEL](https://dadosabertos.aneel.gov.br/pt_BR/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao)). Serve para sinal negativo retrospectivo, com cobertura incompleta de permissionárias e conversão territorial documentada.
- **Defesa Civil Alerta:** histórico/painel pode apoiar marcos temporais, mas não houve API/licença inequívoca localizada; usar referência manual, claramente rotulada.
- **IBGE PEERS:** pesquisa oficial sobre como pessoas foram afetadas nas enchentes de 2024, útil para contexto/impacto, não para instante de detecção ([IBGE](https://www.ibge.gov.br/peers/)). Microdados, quando publicados, exigirão avaliação própria de licença e privacidade.

O conjunto de avaliação deve ser uma tabela derivada e auditável com `source`, `retrieved_at`, `event_time`, `municipality_code`, `measurement`, `license_snapshot` e `known_delay`. A fonte oficial de confirmação não pode participar do score do detector que ela avalia.

## IA, modelos, pesos e datasets

O MVP não precisa de aprendizado profundo nem de um modelo de linguagem. Classificação inicial pode usar categorias e regras versionadas sobre dados sintéticos; isso evita introduzir pesos e corpora de licença incerta.

Para qualquer modelo futuro, o gate de entrada deve registrar separadamente:

- licença e versão do código de inferência;
- licença exata dos pesos/checkpoint e eventuais restrições de uso aceitável, comercial, geográfico ou de alta criticidade;
- proveniência/licença dos datasets de pré-treino e ajuste, inclusive conteúdo social e exclusões;
- termos do serviço se inferência for remota, retenção de prompts e treinamento por provedor;
- cartão do modelo, métricas em português brasileiro, vieses regionais e limitações;
- licença de embeddings/saídas quando prevista e risco de memorização/reidentificação.

Uma etiqueta “open source” ou a licença permissiva da biblioteca não basta. Licenças “research only”, “non-commercial”, SSPL, Commons Clause ou outras *source available* ficam **rejeitadas sem aprovação explícita**. Modelos com termos de uso comportamentais ficam **experimentais** mesmo quando os pesos podem ser baixados. Datasets derivados de redes sociais herdam riscos contratuais, direitos autorais e LGPD; não devem ser incluídos no repositório apenas porque aparecem em artigo acadêmico.

## Regras operacionais de ingestão resultantes

1. Cada adaptador deve exigir um manifesto versionado com `owner`, URL oficial, licença do recurso, termos da API, data de verificação, atribuição, retenção, exclusão/sync, finalidade permitida e decisão.
2. Sem licença/termos claros, o adaptador existe apenas como interface desabilitada e usa fixture sintética.
3. Nenhuma fonte visual/painel será raspada. Captcha, autenticação, robots e controles técnicos não serão contornados.
4. Conteúdo social bruto não entra no dataset de demonstração. Em produção experimental, manter identificador pseudônimo somente se indispensável, texto por TTL mínimo, exclusão propagada e saída agregada por município/célula com limiares.
5. Separar `raw_observation` de atributos derivados; preservar fuso original e UTC, precisão/localização e proveniência.
6. Falha da fonte deve ser observação de saúde do adaptador, nunca evidência automática de desastre. Ausência de posts não implica morte, destruição nem segurança.
7. Nenhum alerta é emitido ou encaminhado. Alertas oficiais são evidências históricas/contextuais e devem exibir tempo de validade.
8. Antes de dados pessoais reais, elaborar RIPD; a ANPD recomenda fazê-lo antes do tratamento para avaliar riscos ([ANPD](https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/relatorio-de-impacto-a-protecao-de-dados-pessoais-ripd)).

## Pendências que exigem validação humana

- Aprovar uma licença definitiva do projeto e uma política separada para dados sintéticos.
- Obter confirmação oficial/licença do recurso específico antes de automatizar INMET, Cemaden, S2iD/Atlas, Defesa Civil Alerta e exports da Anatel.
- Se X for desejado, submeter o caso de uso e revisar contrato/preço/retention policy; nenhuma conta ou aceite foi realizado.
- Definir finalidade/base legal LGPD, papel de controlador/operador, RIPD, canal de direitos, TTL e limiares de agregação antes de qualquer conteúdo social real.
- Escolher infraestrutura de mapa: tiles locais ou provedor contratado/licenciado; não depender do servidor comunitário OSM.
- Revisar implicações de ODbL ao combinar ANEEL/OSM com a base territorial e ao publicar exportações.
- Revalidar todos os links, versões e termos imediatamente antes de produção: termos de API, preços e políticas operacionais podem mudar.

## Registro de incertezas

- Não foram localizados, em páginas oficiais abertas consultadas, termos completos e específicos de API/licença/retention para Cemaden, Defesa Civil Alerta/IDAP e alguns recursos INMET/Anatel/S2iD.
- Declarações institucionais de “dados abertos” sustentam uma candidatura, mas a decisão final deve acompanhar a licença/metadado do arquivo concreto.
- Preço e limites de X, Bluesky, Mastodon, INMET API, ANA API e portais CKAN podem variar; números não foram copiados para evitar falsa estabilidade.
- Esta pesquisa não aceitou termos, criou conta, usou credencial, coletou dados pessoais nem executou scraping.
