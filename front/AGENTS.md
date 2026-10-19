# Frontend React/Vite

Esta pasta contém o frontend do Logos, originado de um protótipo do Figma Make
e agora conectado à API em `back/`. Usa React 19, TypeScript, Vite 8 e Tailwind
CSS 4; consulte o README da raiz para instalação e comandos.

## Arquivos principais

- `src/main.tsx`: monta `App` e importa o CSS global.
- `src/App.tsx`: orquestra filtros, modal, toasts e os hooks.
- `src/types/incident.ts`: tipos e listas de domínio (categorias, criticidades, status).
- `src/api/client.ts`: chamadas `fetch` com `AbortController` e `ApiError` tipado (inclui 409).
- `src/hooks/`: `useIncidents` (lista, filtros, loading/erro/retry) e `useUpdateStatus` (mutação).
- `src/components/`: `Header`, `FilterBar`, `IncidentCard`, `StatusModal`, `Toast`,
  `FeedbackStates`, `Button` e `Badges`.
- `src/index.css`: estilos globais (tema claro/escuro via `.app.dark`).
- `index.html`: documento HTML carregado pelo Vite.
- `vite.config.ts`: React, Tailwind, proxy de `/api` para `http://localhost:8000` e
  utilitários de dev do Figma Make.

## Estilos

Os estilos estão em `src/index.css` com classes semânticas (`incident-card`,
`modal`, `toast-*`); os utilitários do Tailwind não são usados no momento.
Preserve a identidade visual ao alterar componentes.

O servidor de desenvolvimento não é garantido como ativo. Inicie-o com
`npm run dev` (porta 5173) quando necessário, com o backend rodando.
