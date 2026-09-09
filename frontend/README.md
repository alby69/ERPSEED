# ERPSEED Frontend

Interfaccia utente React per la piattaforma ERPSeed.

## Stack

- React 19 + Vite
- Ant Design 5 (UI components)
- react-router-dom v7 (routing)
- Zustand (state management)
- ECharts / ApexCharts (charts)

## Struttura

```
src/
├── assets/         # Immagini ed asset statici
├── components/     # Componenti UI (archetypes, charts, core, ui, workflow, etc.)
├── context/        # Context Providers (AuthContext, ThemeContext, NotificationContext)
├── hooks/          # Custom React hooks (useColumnManager, useResponsive, useCrudData)
├── lib/cashrec/    # Motore CashRec 100% client-side (engine, worker, parser, reporter)
├── locales/        # Traduzioni IT/EN (i18n)
├── pages/          # 50+ pagine applicative (Dashboard, Anagrafiche, Prodotti, CashRec, etc.)
├── stores/         # State management Zustand (workflowBuilderStore)
├── theme/          # Token di design centralizzati (tokens.js)
├── utils/          # Utility (apiFetch, binding, dateUtils, exportUtils)
└── __tests__/      # Test unitari (Vitest + React Testing Library)
```

## Comandi

```bash
npm install        # Installa dipendenze
npm run dev        # Avvia dev server (localhost:5173)
npm run build      # Build produzione
npx eslint src/    # Lint
```

## Documentazione

Vedi [FRONTEND_GUIDE.md](../docs/FRONTEND_GUIDE.md) per la guida sviluppatori.
Vedi [docs/](../docs/) per la documentazione completa del progetto.
