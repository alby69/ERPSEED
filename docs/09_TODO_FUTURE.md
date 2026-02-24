# FlaskERP - Future Improvements & TODO

## ✅ Completati Recentemente

### 🎨 Temi e Personalizzazione
**Stato**: Implementato via **Ant Design ConfigProvider**.
- Aggiunta persistenza del tema nel modello `Project` (primary color, border radius, dark mode).
- Creato `ThemeContext.jsx` per l'applicazione globale dei token di stile.
- Implementata interfaccia admin in `ProjectSettingsPage` per la personalizzazione real-time.

### 🧪 Sistema di Testing Ibrido
**Stato**: Implementato.
- Configurato **Vitest** per test unitari del frontend.
- Integrato **Playwright** nel backend per il test dei moduli dinamici low-code.
- Creato dashboard `TestRunnerPage` per esecuzione e reportistica.

---

## 🚀 Nuove Idee e Miglioramenti Futuri

## 📊 Reporting & Analytics (Priorità Media)

### 2.1 BI Builder Avanzato
**Obiettivo**: Permettere agli utenti di creare dashboard custom via drag & drop.
- Integrare un motore di filtri dinamici per i widget.
- Supportare l'export dei grafici in PDF/PNG.

### 2.2 Reportistica Excel Dinamica
- Generazione automatica di file Excel con pivot basate sui modelli del Builder.

---

## 🤖 AI & Automazione (Priorità Media)

### 3.1 AI-Assisted Builder
- Integrare LLM per generare automaticamente la struttura di un modulo (modelli e campi) partendo da una descrizione testuale (es. "Crea un modulo per la gestione di una biblioteca").

### 3.2 Suggerimenti Intelligenti
- Analisi dei dati di vendita/magazzino per suggerire riordini o identificare trend.

---

## 🛠️ Performance & Scalabilità (Priorità Bassa)

### 4.1 Profiling Automatizzato
- Aggiungere un sistema di profiling delle query SQL lente direttamente nel pannello admin.

### 4.2 Caching Granulare
- Implementare strategie di invalidazione della cache basate su eventi per migliorare i tempi di risposta delle API dinamiche.

---

*Documento aggiornato: Febbraio 2026*
