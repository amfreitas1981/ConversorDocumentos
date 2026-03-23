# TUTORIAL -- Execução Segura do Code Review (Java 21 + Spring Boot 4.x)

## Objetivo

Executar um code review **somente por leitura** no repositório, coletar
evidências (artefatos .txt) e alimentar a IA com um prompt operacional
para obter: - Resumo executivo; - Backlog priorizado (do mais
simples/baixo acoplamento ao mais complexo); - Achados detalhados por
arquivo/classe com plano de correção e riscos; - Checklist consolidado
de conformidade.

## Pré‑requisitos

- Ambiente POSIX (Linux/macOS; no Windows usar Git Bash).
- Ferramentas: `bash`, `grep`, `awk`, `sed`, `find`, `wc`, `sort`,
  `tee`, `zip`.
- Pasta `.review/` ignorada no `.gitignore` (não versionar artefatos de
  revisão).

## Passo 1 --- Preparar a pasta de revisão

1.  Garanta que `.review/` está no `.gitignore`.
2.  Coloque o arquivo **prompt_code_review_java.md** dentro de
    `.review/`.
    - Caso esteja na raiz do repo, o script copiará automaticamente.

## Passo 2 --- Configurar parâmetros do repositório

1.  Execute o script pela primeira vez:

    \$ bash .review/run_review.sh

2.  Ele criará `.review/review.conf`. Edite os campos:

    - ROOT_PACKAGE (ex.: br.com.suaempresa.seuprojeto)
    - MODULES (ex.: :core,:api,:infra) -- opcional
    - BUILD_TOOL (Maven ou Gradle) -- opcional
    - PROFILES (ex.: dev,hml,prod,test)
    - LOG_POLICY (ex.: logback-json+PII-mask+MDC)
    - SEC_POLICY (ex.: OAuth2/JWT+RBAC+headers-segurança)
    - ERROR_STD (ex.: RFC7807)
    - OPENAPI_PATH (se houver arquivo OpenAPI estático)

## Passo 3 --- Coletar artefatos (somente leitura)

1.  Rode novamente o script após editar o `review.conf`:

    \$ bash .review/run_review.sh

2.  O script irá:

    - Inventariar pastas/arquivos;
    - Mapear pacotes, classes, camadas
      (controllers/services/repositories);
    - Rodar heurísticas de *code smells* (Optional.get, System.out,
      EAGER, etc.);
    - Verificar segurança/logs (SecurityFilterChain, @PreAuthorize,
      SLF4J, MDC);
    - Checar configs/profís, OpenAPI estático e endpoints anotados;
    - Validar Build/Qualidade (Java 21 nas configs, plugins de
      qualidade);
    - Gerar artefatos em `.review/artifacts/` e um ZIP em
      `.review/review_artifacts_<DATA>.zip`.

## Passo 4 --- Enviar para a IA (prompt de execução)

1.  Inicie a conversa com a IA e **anexe**:
    - `prompt_code_review_java.md` (o prompt operacional);
    - O ZIP gerado: `review_artifacts_<DATA>.zip` (ou arquivos .txt
      relevantes).
2.  Cole o **prompt de execução** abaixo (ajuste os {{placeholders}}):

--- PROMPT A COLAR NA IA --- Você é um agente de revisão SENIOR para
Java 21 + Spring Boot 4.x, com foco em arquitetura MVC. Siga
**estritamente** as instruções do arquivo **prompt_code_review_java.md**
anexado.

**Contexto do meu repositório:** - Pacote base: {{ROOT_PACKAGE}} -
Módulos: {{MODULES}} - Perfis: {{PROFILES}} - Política de logs:
{{LOG_POLICY}} - Política de segurança: {{SEC_POLICY}} - Padrão de erro:
{{ERROR_STD}} - OpenAPI estático (se houver): {{OPENAPI_PATH}}

**Evidências anexadas (somente leitura):** artefatos gerados pelo script
`.review/run_review.sh`.

**O que produzir agora:** 1) Um **Resumo Executivo** destacando riscos
(segurança, dados, performance, manutenção) e *quick wins*. 2) Um
**Backlog Prioritário** em tabela, do **mais simples/baixo acoplamento**
ao mais complexo/alto risco, com esforço (P/M/G), risco
(Baixo/Médio/Alto), dependências e racional. 3) **Achados detalhados por
arquivo/classe**, no formato do modelo indicado no prompt operacional
(ID, Local, Categoria, Problema, Impacto, Como corrigir \[passo a
passo\], Esforço, Risco, Dependência, Critérios de aceite). 4)
**Checklist consolidado** por camada.

**Regras:** mantenha **equivalência funcional**; proponha **refactors
incrementais** com testes; nunca quebre compatibilidade de API sem plano
de migração. --- FIM DO PROMPT ---

## Passo 5 --- Iterar e aprofundar

- Se a IA indicar áreas críticas, gere lotes adicionais de evidências
  (por módulo/camada) e solicite backlog incremental.
- Peça exemplos de commits/diffs sugeridos (sem executar nada ainda) e
  critérios de teste.

## Boas práticas de segurança

- **Não exponha segredos**: o script redige possíveis chaves/senhas em
  `application*.yml`.
- **Somente leitura**: não há build/execução; todos os comandos são
  grep/find/awk/sed.
- **Auditoria**: os logs ficam em `.review/logs/` e todos os artefatos
  em `.review/artifacts/`.

## Saídas geradas (padrão)

- `.review/artifacts/01_arvore.txt` -- árvore de diretórios (4 níveis)
- `.review/artifacts/10_pacotes.txt` -- lista de pacotes
- `.review/artifacts/20_controllers_annot.txt` / `21_services_annot.txt`
  / `22_repositories_annot.txt`
- `.review/artifacts/30_smells.txt` -- heurísticas (Optional.get,
  System.out, EAGER, etc.)
- `.review/artifacts/40_security_logs.txt` -- segurança/logs
  (SecurityFilterChain, @PreAuthorize, SLF4J/MDC)
- `.review/artifacts/50_configs.txt` -- perfis, propriedades sensíveis
  (redigidas), bindings de config
- `.review/artifacts/60_endpoints_openapi.txt` -- anotações de endpoints
  e presença de OpenAPI
- `.review/artifacts/70_build_quality.txt` -- plugins/flags Java 21
- `.review/review_artifacts_<DATA>.zip` -- pacote pronto para anexar na
  conversa com a IA

## Observações finais

- Se necessário, adapte os greps ao seu padrão de pacotes/nomes de
  pastas.
- Em repositórios grandes, rode por **módulo** e envie à IA por partes.
- Mantenha o arquivo `prompt_code_review_java.md` sempre atualizado com
  suas políticas internas.
