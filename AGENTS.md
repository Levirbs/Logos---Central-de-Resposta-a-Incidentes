# AGENTS.md

# Logos: instruções do projeto

Logos é um MVP para triagem e resposta a incidentes. O frontend React/Vite em
`front/` é um protótipo; backend, API e persistência ainda são planejados.

## Antes de alterar código

- Leia [as decisões de arquitetura e UX](docs/DECISIONS.md) e o README da área
  que será alterada.
- Trate o case integral fornecido pelo usuário como fonte dos requisitos;
  `AGENTS.md` e `docs/DECISIONS.md` são contexto complementar, não substitutos
  do case.
- Preserve o comportamento existente, incluindo filtros, priorização e
  feedback visual, salvo quando a tarefa pedir explicitamente uma mudança.
- Prefira mudanças pequenas e completas; não implemente requisitos planejados
  como se já existissem.

## Fluxo de trabalho

- Planeje cada tarefa em duas passadas: a segunda deve criticar e refinar a
  primeira. Aguarde a aprovação explícita do usuário antes de implementar.
- Use uma branch `feature/<slug>` ou `fix/<slug>` por tarefa independente.
- Mantenha implementação, revisão e correções dessa tarefa na mesma branch.
- Faça a revisão comparando o diff com o case, o plano aprovado e as decisões.
  O Reviewer não deve editar arquivos.
- Se forem necessárias correções, retome a implementação por no máximo duas
  rodadas.
- Não crie commits nem faça push sem autorização explícita do usuário.

## Convenções

- TypeScript estrito; evite `any`.
- Componentes React em PascalCase e funções/variáveis em camelCase.
- Comente apenas quando necessário para explicar o motivo de uma decisão não
  óbvia.
- Use Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `style:`,
  `chore:` ou `test:`); mantenha cada commit em um conceito.
- Não crie commits a menos que solicitado.

## Validação

- Execute os testes e verificações relevantes para a alteração.
- Para mudanças no frontend, use os comandos documentados no
  [README principal](README.md) e verifique os fluxos afetados.