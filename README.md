# Logos — Central de Resposta a Incidentes

MVP para priorizar e acompanhar incidentes de uma central de operações. Um
analista vê a fila ordenada por criticidade e antiguidade, filtra por
criticidade e categoria e altera o status; a API impede que dois analistas
sobrescrevam a mesma alteração (controle otimista por versão, HTTP 409).

## Estrutura

- [`back/`](back/): API FastAPI + SQLAlchemy + SQLite e testes `pytest`.
- [`front/`](front/): interface React, TypeScript e Vite.
- [`docs/DECISIONS.md`](docs/DECISIONS.md): decisões de UX, arquitetura,
  concorrência e resiliência.
- [`AGENTS.md`](AGENTS.md): instruções para agentes de desenvolvimento.

## Como executar

Requer Python 3.13+ e Node.js com npm. Use dois terminais (PowerShell).

### 1. Backend (porta 8000)

```powershell
Set-Location .\back
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Na primeira execução o banco `back/logos.db` é criado e populado com 100
incidentes de exemplo. Documentação interativa em
<http://localhost:8000/docs>. Para recriar os dados: `python -m app.seed --reset`
(dentro de `back/`, com o ambiente virtual ativo).

Testes:

```powershell
Set-Location .\back
python -m pytest
```

### 2. Frontend (porta 5173)

```powershell
Set-Location .\front
npm install
npm run dev
```

Abra <http://localhost:5173>. O Vite encaminha `/api` para
`http://localhost:8000`, então o backend precisa estar rodando.

Outros comandos disponíveis em `front/`:

```powershell
npm run typecheck
npm run build
npm run preview
npm run format
```

Se `front/dist` existir (após `npm run build`), o backend também serve a
interface em <http://localhost:8000>, sem precisar do Vite.

### API

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/v1/incidents?criticality=&category=&status=` | Lista ordenada (máx. 200) |
| `GET` | `/api/v1/incidents/{id}` | Detalhe |
| `POST` | `/api/v1/incidents` | Cria incidente (`code` = `INC-{id:05d}`) |
| `PATCH` | `/api/v1/incidents/{id}` | Altera o status: `{ "status", "version" }` |
| `GET` | `/api/v1/health` | Verificação de saúde e do banco |

Um `PATCH` com `version` desatualizada retorna `409` com
`{ "code": "VERSION_CONFLICT", "message": "...", "current": { ... } }`.

Variáveis opcionais do backend: `LOGOS_DATABASE_URL`, `LOGOS_CORS_ORIGINS`
(padrão `http://localhost:5173`) e `LOGOS_STATIC_DIR`.

O CSS global está em `front/src/index.css`.

## Fluxo de desenvolvimento com Antigravity

Use a Antigravity App, CLI ou integração de IDE autenticada com sua conta
Google. O fluxo é coordenado por você na interface do Antigravity; este
repositório não inclui um orquestrador LangGraph nem uma integração do SDK.
Assim, o uso da conta Pro não depende de uma chave Gemini API.

Para cada tarefa independente:

1. Inicie o Planner com a descrição integral da tarefa e compartilhe
   `AGENTS.md` e `docs/DECISIONS.md` como contexto complementar. Mantenha o case
   completo fora do repositório.
2. Peça ao Planner uma primeira proposta sem editar arquivos; em seguida peça
   uma segunda passada crítica, também sem editar, para encontrar falhas e
   refinar o plano.
3. Revise e aprove o plano explicitamente. Antes da aprovação, nenhum agente
   deve implementar mudanças.
4. Após aprovar, crie uma branch `feature/<slug>` ou `fix/<slug>` a partir da
   branch-base escolhida. Execute Fullstack nessa branch para ajustar o
   frontend e implementar o backend que o case exigir.
5. Em uma sessão de Reviewer separada, forneça o case integral, o plano
   aprovado e o diff. O Reviewer compara a implementação com o case e as
   decisões, sem editar arquivos. Se exigir correções, retome o Fullstack na
   mesma branch; limite o processo a duas rodadas de correção.

Fullstack, Reviewer e eventuais correções permanecem na mesma branch. Revise
as alterações e os testes antes de decidir sobre commits e push; agentes não
devem criar commits por conta própria.

## Estado das decisões

FastAPI, SQLite, a API real e o controle de concorrência por versão/HTTP 409 já
estão implementados. Autenticação e hospedagem na nuvem continuam fora do
escopo atual. Veja [`docs/DECISIONS.md`](docs/DECISIONS.md) antes de alterar
essas partes.
