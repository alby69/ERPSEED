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
├── pages/          # 44 pagine (Dashboard, Anagrafiche, Prodotti, etc.)
├── components/     # 43 componenti riutilizzabili
├── context/        # AuthContext, ThemeProvider
├── locales/        # Traduzioni IT/EN
└── utils/          # apiFetch, helpers
```

## Comandi

```bash
npm install        # Installa dipendenze
npm run dev        # Avvia dev server (localhost:5173)
npm run build      # Build produzione
npx eslint src/    # Lint
```

## Documentazione

Vedi [FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md) per la guida sviluppatori.
Vedi [backend/docs/](../backend/docs/) per la documentazione completa del progetto.
