# Modelo de ameaças

## Escopo e ativos

Ativos: integridade de observações/baselines/hipóteses; condições de uso e proveniência; localização de populações vulneráveis; disponibilidade da análise; confiança do analista. Fronteiras: arquivo de replay não confiável, futuros provedores externos, servidor HTTP local e navegador.

## Ameaças e controles

| Ameaça | Impacto | Controle atual | Próximo controle antes de produção |
|---|---|---|---|
| Replay adulterado ou sem natureza declarada | Inferência enganosa | Esquema mínimo, rótulo obrigatório, limite 10 MiB | Assinatura/hash, schema versionado, autorização do produtor |
| HTML/script em nomes ou conteúdo | XSS e tomada do painel | SVG usa `textContent`; HTML dinâmico escapa texto territorial; sem posts brutos | CSP, sanitizador revisado, testes de payloads |
| Path traversal | Leitura local | Servidor só permite três nomes estáticos enumerados | Framework HTTP endurecido/reverse proxy |
| Arquivo enorme/JSON hostil | Exaustão de memória/CPU | Limite de 10 MiB | Limites por coleção, parser streaming, quotas |
| Fonte indisponível imitando silêncio | Falso desastre | Saúde separada, contribuição reduzida, falha não vira evidência | SLO por adaptador, circuit breaker, múltiplas fontes |
| Bots, duplicação, brigading | Pico falso | Dados sintéticos agregados; posts não ingeridos | Deduplicação, taxa por origem, sinais de coordenação auditáveis |
| Poisoning de baseline | Normalização do desastre/ataque | Calibração separada da avaliação | Janela congelada, robust statistics, revisão/versionamento |
| Geolocalização excessiva | Risco físico/reidentificação | Nível municipal e geometrias esquemáticas | k-anonimato/limiar, generalização, RBAC |
| Exfiltração por logs/telemetria | Vazamento pessoal | Handler não persiste requests | Logging estruturado minimizado e revisão de fornecedores |
| Confiança mal calibrada | Automação indevida | Rótulo “não verificado”, limitações e revisão humana | Calibração histórica, limiares por uso, dupla aprovação |
| Alteração de licença/termos | Uso não autorizado | Data de consulta e manifestos propostos | Monitor de termos com revisão humana; kill switch por fonte |
| Dependência comprometida | Execução arbitrária | Zero pacotes externos; auditoria de imports/SBOM | Pin por hash, scanner de vulnerabilidade e atualização definida |
| Uso do sistema para vigilância | Dano a comunidades | Sem perfis/autores; saída agregada; sem alertas | Política de uso, controle de acesso, auditoria e sanções |

## Abuso de conteúdo

Texto futuro de fonte externa é dado, nunca instrução. Não deve entrar em prompts privilegiados, templates HTML, comandos, logs executáveis ou consultas sem parametrização. Classificadores devem operar em processo restrito e retornar categorias/atributos, não ações. URLs, anexos e mídia ficam desabilitados por padrão.

## Resposta

Ao detectar corrupção, vazamento ou fonte fora dos termos: desabilitar o adaptador, preservar hashes/logs mínimos, marcar hipóteses afetadas, avisar o responsável humano, apagar/sincronizar conforme contrato e registrar a decisão. O produto não continua operando silenciosamente com evidência cuja proveniência foi invalidada.
