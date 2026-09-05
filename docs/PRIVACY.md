# Privacidade, ética e LGPD

**Estado do MVP:** somente dados sintéticos agregados; nenhuma pessoa, publicação, credencial ou coordenada residencial é coletada. Este documento é um projeto de controles, não definição de base legal nem aconselhamento jurídico.

## Princípios vinculantes

- Finalidade limitada a apoio de analistas; sem alerta público, despacho ou decisão automatizada de alto impacto.
- Não criar perfis individuais, identificar autores, exibir mensagens pessoais ou conservar texto bruto na demonstração.
- Agregar por município/célula e suprimir grupos pequenos antes de qualquer saída pública futura.
- Separar precisão territorial de confiança; localização inferida nunca é “exata”.
- Silêncio digital não implica morte, desaparecimento, destruição ou segurança.
- Registrar cobertura, saúde da fonte e desigualdade de conectividade; ausência de fonte não vira ausência de evento.
- Revisão humana obrigatória para hipóteses de alto impacto; trilha de evidências e versão do detector preservadas.

## Gate para dado real

Antes do primeiro tratamento real, o responsável deve aprovar: finalidade e base legal; papéis de controlador/operador; RIPD; encarregado/canal de direitos; contrato e termos de cada fonte; campos mínimos; limiares de agregação; território; segurança; transferências; prazo de retenção; sincronização de alteração/exclusão; resposta a incidente e processo de descarte. Sem esse registro, o adaptador permanece desabilitado.

## Retenção proposta

| Classe | MVP | Produção experimental |
|---|---|---|
| Conteúdo social bruto | Não coletado | Bloqueado até termo/base/TTL aprovados; menor prazo tecnicamente possível |
| Identificador de autor | Não coletado | Evitar; pseudonimizar apenas se indispensável e apagar com a origem |
| Observação física agregada | Sintética | Conforme licença/finalidade e política da fonte |
| Baseline e inferência municipal | Recalculável | Prazo documentado por finalidade, com versão e direito de contestação |
| Logs | Sem IP persistente no servidor MVP | Minimização, controle de acesso e prazo curto aprovado |

## Direitos, exclusão e qualidade

Uma futura fonte social deve consumir eventos de edição/exclusão quando disponíveis e manter índice reverso mínimo para apagar derivados vinculáveis. Correções de sensores e limites territoriais geram nova versão, sem sobrescrever silenciosamente o histórico usado numa inferência. Saídas devem identificar natureza real/simulada/inferida, horário, cobertura, limitações e canal de revisão.

## Viés e segurança comunitária

Cobertura digital varia por renda, idade, operadora, idioma, acessibilidade, ruralidade e crise. O baseline deve medir cobertura e não usar volume populacional bruto como neutralidade. Detectores futuros devem avaliar bots, duplicação e campanhas coordenadas sem converter essa análise em perfil de indivíduos. Coordenadas raras, abrigos, hospitais e infraestrutura sensível devem receber generalização e controle de acesso.

Referências oficiais atuais e consulta de LGPD/ANPD estão registradas em `docs/research/SOURCE_RESEARCH.md`.
