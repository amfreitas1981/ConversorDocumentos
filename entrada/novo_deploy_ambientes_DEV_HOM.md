# Novo Deploy nos ambientes DEV e HOM

---

## 1) Identificar exatamente “o que não funciona” (para não tentar corrigir no escuro)

Você consegue me dizer qual destes cenários é o seu?

1. **A aplicação nem sobe** no DEV/HOM (CrashLoopBackOff / erro de start).
2. **Sobe, mas o scheduler não roda** (não gera SW).
3. **Roda e tenta gerar, mas falha no upload S3** (AccessDenied / key inválida / bucket errado).
4. **Gera SW, mas com conteúdo/layout incorreto** (regra de negócio).
5. **Ainda existe alguma execução do FE no ambiente** (por config/pipeline/job externo) e isso quebra o fluxo.

Sem isso eu consigo orientar, mas para fechar o diagnóstico com precisão eu vou precisar de **logs** do pod (ou logs do job) do momento da falha.

---

## 2) Validar se ainda existe “resto” de FE no repositório (código/config)

Mesmo você tendo removido a geração FE, o ambiente pode estar com:

- propriedades antigas tipo `atm.export.fe-*`
- secrets/ConfigMap ainda injetando essas variáveis
- chart values ainda referenciando FE
- algum “passo” no pipeline esperando FE como artefato

O seu deploy é via IU Pipes/TechStacks (tem `.iupipes.yml` e values por ambiente em `app/_techstack/values_dev.yml` e `values_hom.yml`).

**Ação:** conferir e limpar qualquer referência a FE em:
- `app/_techstack/values_dev.yml`
- `app/_techstack/values_hom.yml`
- `app/src/main/resources/application*.yml` (se existirem overrides)
- secrets/configmaps do ambiente (K8s) que injetem variáveis `ATM_EXPORT_FE_*`

Se você me mandar o conteúdo de `values_dev.yml` e `values_hom.yml` (ou me autorizar a eu buscar aqui), eu aponto exatamente o que ajustar.

---

## 3) Fazer o ambiente “esquecer” o deploy antigo (o passo que normalmente resolve)

Em TechStacks, quando um deploy anterior tinha recursos/variáveis e agora o chart/values mudou, às vezes fica “sobra” (ConfigMap, Secret, env var, etc.) ou o rollout não troca tudo do jeito esperado.

Na sua pipeline existe a opção:

- `.iupipes.yml` → `deploy.k8s.destroy: "false"`

**Para forçar limpeza completa (recomendado neste caso):**
1. Rodar um deploy com `destroy: "true"` **para todos os ambientes instalados** (primeiro), para remover recursos antigos.
2. Depois rodar deploy normal com `destroy: "false"` já com os values corrigidos.

Isso costuma resolver exatamente o caso “código mudou mas ambiente continua se comportando como antes”.

> Importante: “destroy” derruba a app e recria. Planeje janela.

---

## 4) Garantir que o deploy está pegando a branch certa e gerando nova imagem

O workflow do repositório indica:

- feature branches (`feature**`) disparam build/PR
- merge (PR fechado) em `develop` dispara workflow `2 - [DEV] Build & Deploy`

Então para DEV/HOM atualizar de verdade:
- confirme que o PR foi **mergeado em `develop`** (o `develop` atual está no commit `64fb136...`)
- confirme que o workflow `2-develop.yml` executou até o fim
- confirme que a imagem/tag que está no cluster é a nova (não reaproveitando cache)

Se o pipeline estiver “usando cache” e publicando a mesma tag, você pode ver o comportamento “antigo” mesmo com código novo.

---

## 5) Checklist de configuração mínima para “somente SW” (DEV/HOM)

Garanta no values/env do deployment:

- `ATM_EXPORT_ENABLED=true` (ou não setar, pois default é `true`)
- `ATM_EXPORT_CRON=0 0 2 * * *` (ou o cron desejado)
- `ATM_EXPORT_SW_FILE_NAME=SW25N` (ou o nome exigido)
- `ATM_EXPORT_SW_S3_KEY=export/sw/RPX.DR.A056A` (ou o path exigido)
- `ATM_EXPORT_ENCODING=ISO-8859-1`
- Credenciais/IRSA/permissão para `s3:PutObject` no bucket/key do SW
- E **não existir nenhuma variável `ATM_EXPORT_FE_*`** sendo injetada (se existir, remova para evitar o app tentar bindar config inexistente ou algum fluxo legado externo)

---
