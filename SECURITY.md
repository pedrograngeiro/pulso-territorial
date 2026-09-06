# Segurança

O projeto é experimental e mantém correções na branch main. Não há prazo contratual de resposta.

Para uma vulnerabilidade, use [Report a vulnerability](https://github.com/pedrograngeiro/pulso-territorial/security/advisories/new). Informe versão/commit, impacto e passos de reprodução sem incluir credenciais reais. Evite publicar detalhes exploráveis em uma issue aberta antes da análise.

Por padrão o servidor escuta apenas em 127.0.0.1. A aplicação não implementa autenticação para hospedagem pública. Tokens ficam no ambiente do backend; a distribuição estática não contém consumidores em execução nem segredos.

Problemas de qualidade/cobertura dos dados e ausência de medição devem ser relatados em issues comuns, sem dados pessoais.
