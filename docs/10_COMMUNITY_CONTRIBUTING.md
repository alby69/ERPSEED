# ERPaaS - Guida Contributing e Community

## Documento #10 - Community, Licenza e Contributing

---

## 1. Open Source Strategy

### 1.1 Dual Licensing

```
┌─────────────────────────────────────────────────────────────┐
│                    FLASKERP ECOSYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  FLASKERP CORE                      │   │
│   │            (MIT License - Open Source)              │   │
│   │   • Core multi-tenant                              │   │
│   │   • Moduli base                                    │   │
│   │   • API REST                                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│           ┌─────────────┴─────────────┐                    │
│           ▼                           ▼                    │
│   ┌───────────────────┐    ┌───────────────────┐          │
│   │   FLASKERP PRO    │    │   SAAS PLATFORM    │          │
│   │  (Proprietary)    │    │    (Subscription)   │          │
│   ├───────────────────┤    ├───────────────────┤          │
│   │ • Enterprise      │    │ • Hosting          │          │
│   │   Features        │    │ • Support          │          │
│   │ • White-label     │    │ • Updates          │          │
│   │ • SLA             │    │ • Multi-tenant     │          │
│   └───────────────────┘    └───────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Cosa è Open Source

| Componente | License | Usage |
|------------|---------|-------|
| Core Engine | MIT | Free use, modify, distribute |
| Base Modules | MIT | Free use |
| Documentation | CC BY 4.0 | Attribution required |
| Logo/Brand | Proprietary | No use without permission |

### 1.3 Cosa è Proprietario

| Componente | Accesso |
|------------|---------|
| SaaS Platform | Solo abbonati |
| Enterprise Features | Solo licenza enterprise |
| Supporto prioritario | Solo abbonati |
| Marketplace (futuro) | 20% commissione |

---

## 2. Community Structure

### 2.1 Canali di Comunicazione

| Canale | Scopo | Link |
|--------|-------|------|
| **GitHub Discussions** | Q&A, idee | github.com/flaskerp/flaskerp/discussions |
| **GitHub Issues** | Bug report | github.com/flaskerp/flaskerp/issues |
| **Discord** | Chat in tempo reale | discord.gg/flaskerp |
| **Newsletter** | Update mensili | flaskerp.com/newsletter |
| **Blog** | Tutorial, annunci | flaskerp.com/blog |

### 2.2 Ruoli Community

| Ruolo | Descrizione | Privilegi |
|-------|------------|-----------|
| **User** | Utilizzatore base | Leggi, scarica |
| **Contributor** | Chi contribuisce codice | PR, issues |
| **Maintainer** | Core contributor | Review, merge |
| **Partner** | Consulenti/Agency | Early access, supporto |

### 2.3 Supporto

| Livello | Canale | Tempo Risposta |
|---------|--------|----------------|
| **Community** | GitHub Discussions | 48-72h |
| **Community** | Discord | 24-48h |
| **Pro** | Email | 24h |
| **Enterprise** | Phone/Slack | 4h |

---

## 3. Contributing Guide

### 3.1 Come Contribuire

```bash
# 1. Fork del repository
# https://github.com/flaskerp/flaskerp/fork

# 2. Clona il fork
git clone https://github.com/YOUR_USERNAME/flaskerp.git
cd flaskerp

# 3. Crea branch per feature
git checkout -b feature/amazing-feature

# 4. Fai le modifiche
# ...codice...

# 5. Commit con messaggi chiari
git commit -m "feat: add amazing feature"

# 6. Push al fork
git push origin feature/amazing-feature

# 7. Apri Pull Request
# https://github.com/flaskerp/flaskerp/compare
```

### 3.2 Regole Commit

Usiamo **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: Nuova feature
- `fix`: Bug fix
- `docs`: Documentazione
- `style`: Formattazione
- `refactor`: Code refactoring
- `test`: Test
- `chore`: Manutenzione

**Examples**:
```bash
git commit -m "feat(parties): add validation for Italian VAT number"
git commit -m "fix(sales): resolve order total calculation bug"
git commit -m "docs: update API documentation"
```

### 3.3 Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] Added tests for new functionality

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### 3.4 Code Style

```bash
# Python (Black + Ruff)
black .
ruff check --fix .

# JavaScript/TypeScript (Prettier)
npm run format
npm run lint
```

**Regole**:
- Max line length: 100
- Docstrings: Google style
- Type hints: obbligatori
- No commented code

---

## 4. Code of Conduct

### 4.1 Our Pledge

We welcome everyone who participates in FlaskERP. By participating, you agree to maintain a respectful environment.

### 4.2 Standards

**Positive behavior**:
- Using welcoming language
- Being respectful of viewpoints
- Accepting constructive criticism gracefully
- Focusing on what's best for the community

**Negative behavior**:
- Harassment of any kind
- Inappropriate language
- Personal attacks
- Publishing others' private information

### 4.3 Enforcement

Violations should be reported to `conduct@flaskerp.com`. All complaints will be reviewed and investigated.

---

## 5. Licenza

### 5.1 MIT License Summary

```
MIT License

Copyright (c) 2026 FlaskERP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software... (see full license)
```

### 5.2 Full License

Vedi: `LICENSE` file nel repository

### 5.3 Trademark Policy

"FlaskERP" è un marchio registrato. Non puoi:
- Usare il logo senza permesso
- Usare il nome per prodotti derivati
- Indicare che il tuo prodotto è "ufficiale"

---

## 6. Roadmap e Priorità

### 6.1 Come le feature vengono decise

```
1. Community Request (Discord/GitHub)
         ↓
2. Discussion & Upvotes
         ↓
3. Maintainer Review
         ↓
4. Prioritization (Impact vs Effort)
         ↓
5. Added to Backlog/Milestone
         ↓
6. Development
```

### 6.2 Come proporre feature

```markdown
## Feature Request Template

**Feature Description**
Clear description of the feature

**Problem Solved**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other solutions?

**Additional Context**
Screenshots, examples, etc.
```

---

## 7. Sponsorizzazioni

### 7.1 Open Collective

Via Open Collective: opencollective.com/flaskerp

### 7.2 Sponsor Levels

| Level | Amount | Benefits |
|-------|--------|----------|
| **Supporter** | €10/mese | Badge, early access |
| **Sponsor** | €50/mese | Logo on site, priority |
| **Partner** | €200/mese | Dedicated support |

### 7.3 Come Usare i Fondi

- Infrastructure (server, domains)
- Development time
- Documentation
- Community events

---

## 8. FAQ

### 8.1 Posso usare FlaskERP per i miei clienti?

**Sì**, puoi:
- Installarlo per i tuoi clienti
- Personalizzarlo
- Offrire supporto

**No**, non puoi:
- Rivendere il codice
- Usare il brand "FlaskERP" come tuo
- Offrire come SaaS senza licenza

### 8.2 Come funziona la licenza Enterprise?

Contatta `enterprise@flaskerp.com` per:
- White-label completo
- SLA garantiti
- Supporto dedicato
- Source code access

### 8.3 Posso contribuire in modo non tecnico?

**Sì**! Puoi:
- Tradurre documentazione
- Segnalare bug
- Creare tutorial
- Aiutare altri utenti
- Promuovere il progetto

---

## 9. Contatti

| Tipo | Contatto |
|------|----------|
| Generale | hello@flaskerp.com |
| Commerciale | sales@flaskerp.com |
| Enterprise | enterprise@flaskerp.com |
| Security | security@flaskerp.com |
| Conduct | conduct@flaskerp.com |

---

## 10. Risorse per Iniziare

### 10.1 Good First Issues

Cerca label: `good first issue`

### 10.2 Documentazione

- Quick Start: `docs/QUICKSTART.md`
- API Reference: `docs/API.md`
- Module Development: `docs/MODULES.md`

### 10.3 Ambiente di Sviluppo

```bash
# Setup ambiente
make setup

# Run tests
make test

# Run locally
make run
```

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #10 - Community e Contributing*
