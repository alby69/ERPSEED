# FlaskERP - Future Improvements & TODO

## 🎨 Temi e Personalizzazione (Priorità Alta)

### 1.1 Gestione Temi Grafici
**Obiettivo**: Permettere agli amministratori di cambiare l'aspetto dell'ERP senza modificare il codice.
**Soluzione Consigliata**: Utilizzare **Ant Design ConfigProvider**.
- **Perché**: Ant Design permette di iniettare un oggetto `theme` (token) che controlla colori primari, bordi, font e modalità (light/dark) in modo globale. È la soluzione più semplice da estendere e mantenere.
- **Implementazione**:
  - Aggiungere una tabella `sys_settings` o estendere `projects` con campi per i colori (es. `primary_color`, `border_radius`).
  - Creare un context React `ThemeContext` che recupera queste impostazioni all'avvio.
  - Avvolgere l'intera applicazione in `<ConfigProvider theme={userTheme}>`.

---

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
