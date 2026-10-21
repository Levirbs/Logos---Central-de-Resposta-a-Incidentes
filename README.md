# Logos — Central de Resposta a Incidentes

MVP para priorizar e acompanhar incidentes de uma central de operações. Um
analista vê a fila ordenada por criticidade e antiguidade (com incidentes
`Fechado` ao final), filtra pelos 3 seletores — criticidade, categoria e status
(abrindo por padrão nos incidentes `"Aberto"` para priorizar a fila de triagem
imediata) — e altera o status; a API impede que dois analistas sobrescrevam a
mesma alteração (controle otimista por versão, HTTP 409).

## 🌐 Demonstração Online

A aplicação está publicada na nuvem e pronta para uso imediato, sem necessidade de instalação local:

- **Aplicação Web:** <https://logos-rkbs.onrender.com>
- **Documentação da API (Swagger):** <https://logos-rkbs.onrender.com/docs>
- **Health Check:** <https://logos-rkbs.onrender.com/api/v1/health>

> *Nota:* Hospedado no plano gratuito do Render. Caso o serviço esteja em hibernação (*cold start*), a primeira requisição pode levar ~40 segundos para inicializar o container e popular os dados de exemplo. As requisições seguintes respondem em tempo real.

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


## Decisões de arquitetura

As justificativas técnicas detalhadas (controle de concorrência otimista com version/HTTP 409, ordenação no banco, resiliência e metodologia de desenvolvimento) estão documentadas em [docs/DECISIONS.md](docs/DECISIONS.md).
