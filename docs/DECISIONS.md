# Decisões de arquitetura e UX

Registro das decisões do MVP Logos — Central de Resposta a Incidentes. Os
status indicam o que já está implementado e o que continua planejado.

## Objetivo

Permitir que analistas identifiquem e priorizem cerca de 100 incidentes com
rapidez, mantendo integridade nas atualizações e resiliência no fluxo de
atendimento.

## Stack

| Área | Decisão | Status |
| --- | --- | --- |
| Frontend | Vite, React, TypeScript e CSS | Implementado em `front/`, consumindo a API |
| Backend | FastAPI, SQLAlchemy, Pydantic e Uvicorn | Implementado em `back/` |
| Persistência | SQLite (WAL, `busy_timeout=5000`) | Implementado |
| Concorrência | `version` + HTTP 409 | Implementado |
| Autenticação | — | Não implementada |

## Metodologia de desenvolvimento e arquitetura de agentes

Para conduzir a entrega com alto padrão de engenharia de software e inteligência artificial aplicada, estruturei o desenvolvimento utilizando uma arquitetura multiagente coordenada por um **Orquestrador**, com segregação estrita de papéis entre subagentes especializados e aprovação humana em cada etapa (*human-in-the-loop*):

### Papéis e responsabilidades

| Papel / Agente | Modo de operação | Responsabilidade e escopo |
| :--- | :--- | :--- |
| **Orquestrador** | Coordenação | Gerenciou o fluxo do ciclo de vida, preparou as diretrizes de cada fase e garantiu que nenhum agente executasse ações fora do seu escopo (sem implementar código diretamente nem commitar sem autorização). |
| **Planner** | Somente leitura | Analisou os requisitos do case e formulou o plano técnico em **duas passadas** (uma proposta inicial e uma segunda rodada de crítica rigorosa para mitigar riscos de concorrência, TOCTOU e resiliência de rede). |
| **Fullstack** | Leitura e escrita | Atuou na branch isolada `feature/api-integracao`, implementando o backend FastAPI com SQLite WAL, modularizando o frontend React/TS (preservando o visual do Figma) e escrevendo os 26 testes automatizados. |
| **Reviewer** | Somente leitura | Sessão independente de auditoria de código que comparou o diff contra os requisitos do case, avaliou a robustez do HTTP 409 e emitiu o parecer formal (`APPROVED`), sugerindo refinamentos pontuais de UX. |

### Fluxo executado na prática

1. **Planejamento em duas passadas (Planner):** Acionei o Planner com o case completo; na primeira passada ele desenhou a arquitetura e na segunda criticou a si mesmo, refinando o controle de concorrência por `version` e o tratamento de 503 com `Retry-After`.
2. **Aprovação do plano:** Revisei e aprovei formalmente o plano técnico consolidado antes de iniciar qualquer alteração de código.
3. **Isolamento de branch:** Criei a branch `feature/api-integracao` para garantir rastreabilidade completa e isolamento de contexto.
4. **Implementação (Fullstack):** O agente Fullstack construiu a API, os modelos, schemas, seed determinístico de 100 incidentes e conectou os estados reais do frontend.
5. **Revisão e refinamento (Reviewer + Fullstack):** Submeti o diff ao Reviewer, que emitiu veredito `APPROVED` (nota 98/100) e sugeriu a adição do seletor de status e despriorização de incidentes `Fechado`. Conduzi rodadas rápidas com o Fullstack para aplicar e validar essas melhorias.
6. **Versionamento semântico:** Estruturei o histórico em commits atômicos conceituais seguindo Conventional Commits (`feat:`, `test:`, `refactor:`, `docs:`) e realizei o merge para a branch `main`.

## UX e priorização

- Ordenar por criticidade decrescente (`Alta` > `Média` > `Baixa`) e, dentro de
  cada nível, pelos incidentes mais antigos primeiro.
- Apresentar incidentes em cards verticais com barra lateral colorida e badges
  com texto explícito.
- Exibir estados de carregamento com skeleton, lista vazia e erro com opção de
  tentar novamente.
- Mostrar o contexto completo no modal e permitir alterar o status com
  opções de rádio.
- Fechar o modal com `Esc` ou clique fora; manter indicações visuais de
  interatividade.
- Oferecer modos claro e escuro.

A tela consome a API real (`/api/v1`). Os filtros de criticidade, categoria e
status são enviados ao servidor (o filtro de status abre por padrão em `Aberto`
para priorizar a fila de triagem imediata, permitindo alternar para qualquer
outro status ou `"Todos os status"`); o frontend não reordena a lista.

### Ordenação no banco

A ordenação é feita pelo SQLite, não pelo cliente:
`ORDER BY CASE WHEN status = 'Fechado' THEN 1 ELSE 0 END, CASE criticality WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 ELSE 3 END, created_at ASC, id ASC LIMIT 200`. Isso garante que incidentes ativos tenham prioridade visual (Fechados ao final da fila) e mantém uma única fonte da regra de
prioridade sem reordenar no navegador. O
`id` desempata incidentes com o mesmo `created_at`, tornando a ordem estável. O
limite de 200 registros protege a API; o MVP trabalha com cerca de 100.

## Integridade e concorrência

- Cada incidente tem uma `version`. O `PATCH` envia `{ status, version }` e a
  API executa uma única instrução:
  `UPDATE incidents SET status, version = version + 1, updated_at WHERE id = :id
  AND version = :version AND status != :status`. Não há *Last Write Wins* nem
  janela entre ler e escrever.
- Se nenhuma linha for afetada, a API relê o incidente: sem registro, `404`;
  com versão diferente, `409 Conflict` com
  `{ "code": "VERSION_CONFLICT", "message": "...", "current": <incidente> }` na
  raiz da resposta, para o cliente substituir o item sem outra chamada.
- Mesmo status e versão atual: operação sem efeito (`200`, a versão **não**
  aumenta), para não gerar conflitos desnecessários para outros analistas. Mesmo
  status com versão desatualizada continua retornando `409`.
- **Transição de status livre:** qualquer status pode ir para qualquer outro,
  inclusive reabrir um incidente `Fechado`. A proteção do ciclo de vida é a
  versão, não um grafo de transições; restringir transições exigiria uma regra
  de negócio que o case não define.
- A interface desabilita Salvar quando o status não mudou e durante o envio. A
  regra do servidor cobre chamadas diretas e outros clientes.
- Ao receber `409`, o frontend mostra um aviso ("Incidente atualizado por outro
  analista"), fecha o modal e substitui o item na lista pelo `current` devolvido.
- Falhas de rede ou `5xx` no `PATCH` mantêm o modal aberto, exibem erro e não
  alteram a lista (sem atualização otimista).
- Datas são gravadas em UTC e serializadas com `Z`, para o navegador converter
  para o fuso local sem deslocamento.

## Resiliência

- SQLite em modo WAL com `busy_timeout=5000`: leituras não bloqueiam a escrita
  e uma escrita simultânea espera até 5 s pelo lock em vez de falhar.
- Erros operacionais do banco viram `503` com `code: DATABASE_UNAVAILABLE` e
  `Retry-After`; `GET /api/v1/health` verifica o banco.
- O cliente HTTP usa `AbortController`: a busca anterior é cancelada ao trocar
  filtros ou desmontar a tela, e respostas atrasadas são descartadas.
- "Atualizar" mantém a lista visível enquanto recarrega; o skeleton aparece só
  na carga inicial e na troca de filtros.

## Segurança básica

Validação estrita com Pydantic (`extra="forbid"`, limites de tamanho, enums),
SQL parametrizado, CORS restrito à origem de desenvolvimento
(`LOGOS_CORS_ORIGINS` para alterar) e limite fixo de listagem. Não há
autenticação nem autorização; isso está fora do escopo do MVP.

## Convenções

- Usar TypeScript estrito, componentes em PascalCase e funções/variáveis em
  camelCase.
- Comentar apenas quando necessário para explicar o motivo de uma decisão não
  óbvia.
- Preservar filtros, ordenação e feedback visual ao evoluir a interface.
- Seguir Conventional Commits e manter cada commit focado em um conceito.

## Próximas implementações

1. Autenticação e identificação do analista nas alterações.
2. Atualização da lista em tempo quase real (polling ou SSE).
3. Hospedagem na nuvem e migração para um banco servidor se houver múltiplas
   instâncias da API.
