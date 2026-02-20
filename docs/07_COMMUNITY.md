# FlaskERP - Community e Contributing

## Open Source Strategy

### Dual Licensing

```
┌────────────────────────────────────────────────┐
│              FLASKERP ECOSYSTEM                 │
├────────────────────────────────────────────────┤
│   ┌────────────────────────────────────────┐  │
│   │           FLASKERP CORE                 │  │
│   │      (MIT License - Open Source)        │  │
│   └────────────────────────────────────────┘  │
│                      │                         │
│        ┌─────────────┴─────────────┐          │
│        ▼                             ▼          │
│  ┌───────────┐             ┌───────────────┐  │
│  │   PRO     │             │   SAAS        │  │
│  │(Proprietary)           │ (Subscription) │  │
│  └───────────┘             └───────────────┘  │
└────────────────────────────────────────────────┘
```

### Cosa è Open Source

| Componente | License |
|------------|---------|
| Core Engine | MIT |
| Base Modules | MIT |
| Documentation | CC BY 4.0 |

---

## Canali di Comunicazione

| Canale | Scopo |
|--------|-------|
| GitHub Discussions | Q&A, idee |
| GitHub Issues | Bug report |
| Discord | Chat in tempo reale |
| Newsletter | Update mensili |

---

## Come Contribuire

### 1. Fork e Clone

```bash
git clone https://github.com/YOUR_USERNAME/flaskerp.git
cd flaskerp
```

### 2. Crea Branch

```bash
git checkout -b feature/amazing-feature
```

### 3. Commit (Conventional Commits)

```
<type>(<scope>): <description>

Types:
- feat: Nuova feature
- fix: Bug fix
- docs: Documentazione
- refactor: Code refactoring
- test: Test
```

Esempi:
```bash
git commit -m "feat(parties): add validation for Italian VAT"
git commit -m "fix(sales): resolve order total calculation"
git commit -m "docs: update API documentation"
```

### 4. Pull Request

- Apri PR su GitHub
- Segui il template
- Assicurati che i test passino

---

## Code of Conduct

**Comportamento positivo**:
- Linguaggio accogliente
- Rispetto per opinioni diverse
- Accettazione critica costruttiva

**Comportamento negativo**:
- Molestie
- Attacchi personali
- Pubblicazione info private

---

## FAQ

### Posso usare FlaskERP per i miei clienti?

**Sì**:
- Installarlo
- Personalizzarlo
- Offrire supporto

**No**:
- Rivendere il codice
- Usare il brand senza permesso

### Posso contribuire in modo non tecnico?

**Sì**! Tradurre documentazione, segnalare bug, creare tutorial.

---

*Documento aggiornato: Febbraio 2026*
