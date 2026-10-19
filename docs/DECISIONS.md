# Decisões de arquitetura e UX

Registro das decisões do MVP Logos — Central de Resposta a Incidentes. Os
status distinguem o comportamento do protótipo das escolhas que ainda precisam
ser implementadas.

## Objetivo

Permitir que analistas identifiquem e priorizem cerca de 100 incidentes com
rapidez, mantendo integridade nas atualizações e resiliência no fluxo de
atendimento.

## Stack

| Área | Decisão | Status |
| --- | --- | --- |
| Frontend | Vite, React, TypeScript e CSS | Protótipo em `front/` |
| Backend | FastAPI, SQLAlchemy, Pydantic e Uvicorn | Planejado |
| Persistência | SQLite | Planejado |

## Fluxo de trabalho

- O case integral é a fonte dos requisitos e deve permanecer fora do
  repositório. `AGENTS.md` e este documento são contexto complementar.
- O plano é elaborado e criticado em duas passadas. A implementação requer
  aprovação explícita do usuário.
- Cada tarefa independente usa uma branch `feature/<slug>` ou `fix/<slug>`.
  Implementação, revisão e correções permanecem nessa branch.
- A revisão compara o diff com o case, o plano aprovado e estas decisões, sem
  alterar arquivos.
- São permitidas no máximo duas rodadas de correção após a revisão.
- Commits e push exigem autorização explícita do usuário.

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

O protótipo contém a tela e interações com dados locais; isso não significa que
os estados estejam conectados a uma API real.

## Integridade e concorrência

- Na API futura, cada incidente terá uma `version`. Um `PATCH` deve comparar a
  versão recebida com a atual; se divergirem, responder HTTP `409 Conflict`;
  se coincidirem, atualizar o registro e incrementar a versão na mesma
  operação. Não usar *Last Write Wins*.
- Desabilitar Salvar quando o status não mudou e durante o envio.
- O conflito de `INC-00118` ao tentar fechar é apenas uma simulação do
  protótipo; a API deve substituir essa simulação quando implementada.

## Convenções

- Usar TypeScript estrito, componentes em PascalCase e funções/variáveis em
  camelCase.
- Comentar apenas quando necessário para explicar o motivo de uma decisão não
  óbvia.
- Preservar filtros, ordenação e feedback visual ao evoluir a interface.
- Seguir Conventional Commits e manter cada commit focado em um conceito.

## Próximas implementações

1. Desabilitar Salvar quando não houver alteração.
2. Criar backend FastAPI com persistência SQLite e controle otimista de
   concorrência.
3. Conectar o frontend à API e substituir os dados/conflitos simulados.
