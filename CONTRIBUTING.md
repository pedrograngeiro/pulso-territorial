# Contribuir com Pulso Territorial

Abra uma issue para propor uma mudança de escopo ou relatar um problema reproduzível. Para uma correção pequena, um pull request com contexto e validação é suficiente.

## Desenvolvimento

Python 3.13 e Node.js 22 para os testes; o site usa apenas a biblioteca padrão Python e APIs nativas do navegador.

```sh
git clone https://github.com/pedrograngeiro/pulso-territorial.git
cd pulso-territorial
python run.py
```

```sh
python -X utf8 tools/verify.py
node --test tests/frontend.test.mjs tests/monitoring.test.mjs
python tools/build_site.py
```

Os testes não consultam APIs externas. Credenciais são necessárias somente para executar fontes que exigem autenticação, como Cloudflare Radar. Caches, tokens e arquivos de ambiente locais não devem acompanhar contribuições.

Preserve a distinção entre dados reais e simulação, falha de fonte e falta de observação, amostra municipal e cobertura do município inteiro. Uma medição de conectividade não confirma desastre. Inclua um teste que demonstre a correção quando alterar essas regras.

Use commits Conventional Commits, com um propósito por commit. Contribuições de material próprio são submetidas sob Apache-2.0; conteúdo de terceiros precisa de licença e atribuição documentadas. Consulte NOTICE e THIRD_PARTY_NOTICES.md.
