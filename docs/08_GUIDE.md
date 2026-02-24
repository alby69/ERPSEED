# FlaskERP - Guide

## Builder Manuale

Il **Builder** permette di creare e modificare entità direttamente dall'interfaccia web senza scrivere codice.

---

## Gestione Progetti

### Creare un Nuovo Progetto

1. Accedi come Admin
2. Vai su **Admin → Progetti**
3. Clicca **Nuovo Progetto**
4. Compila:
   - Nome progetto
   - Descrizione
   - Scegli template (vuoto o predefinito)
5. Clicca **Crea**

---

## Creare un Modello (Tabella)

### 1. Nuovo Modello

1. Vai su **Builder → Modelli**
2. Clicca **Nuovo Modello**
3. Compila:
   - Nome (es: "Prodotti")
   - Tabella DB (es: "prodotti")
   - Descrizione

### 2. Aggiungi Campi

Clicca **Aggiungi Campo** e configura:

| Tipo | Uso |
|------|-----|
| **string** | Testo breve |
| **text** | Testo lungo |
| **integer** | Numero intero |
| **decimal** | Numero decimale |
| **boolean** | Sì/No |
| **date** | Data |
| **datetime** | Data e ora |
| **select** | Menu a tendina |
| **relation** | Relazione ad altro modello |

### 3. Opzioni Campo

- **Label**: Nome visualizzato
- **Required**: Obbligatorio
- **Unique**: Valore univoco
- **Default**: Valore predefinito
- **Options**: Opzioni per select

---

## Generare Tabella Database

Dopo aver creato/modificato un modello:

1. Vai su **Builder → Modelli**
2. Seleziona il modello
3. Clicca **Genera Tabella**
4. Conferma

Il sistema crea automaticamente la tabella nel database.

---

## Gestione Permessi (ACL)

### Livelli

| Livello | Descrizione |
|---------|-------------|
| **Admin** | Accesso completo |
| **Editor** | Crea, modifica, legge |
| **Viewer** | Solo lettura |

### Assegna Permessi

1. Modello → **Permessi**
2. Aggiungi ruolo
3. Seleziona azioni consentite

---

## Tipi di Campo Avanzati

### Relation (Relazione)

```yaml
# Esempio: Ordine ha relazione con Cliente
campo: cliente
tipo: relation
target: Clienti
```

Crea automaticamente dropdown con i record del modello collegato.

### Calculated (Campo Calcolato)

```yaml
# Esempio: Totale = Quantità × Prezzo
campo: totale
tipo: calculated
formula: quantita * prezzo_unitario
```

### Summary (Riepilogo)

```yaml
# Esempio: Numero ordini per cliente
campo: num_ordini
tipo: summary
target: Ordini
aggregation: count
```

---

## Best Practices

1. **Nomi chiari**: Usa nomi descriptivi per modelli e campi
2. **Validazione**: Imposta campi required dove necessario
3. **Relazioni**: Definisci le relazioni tra modelli
4. **Test**: Prova il modello prima di metterlo in produzione
5. **Backup**: Fai backup prima di modifiche strutturali

---

## Sistema di Testing

MakeERP include un sistema di testing integrato per verificare la correttezza dei moduli.

### 1. Test Unitari (Core)
Per gli sviluppatori che modificano il codice sorgente:
1. Entra nella cartella `frontend/`
2. Esegui `npm run test` per avviare Vitest in modalità watch.
3. Esegui `npm run test:run` per un'esecuzione singola.

### 2. Test Moduli (User-defined)
Per gli amministratori che creano nuovi moduli:
1. Vai su **Admin → Test Runner**
2. Clicca su **Genera Suite** per creare automaticamente test CRUD per un modulo.
3. Clicca su **Esegui** per avviare i test.
4. Per test complessi dell'interfaccia, seleziona il tipo di test **UI (Playwright)**. Questi test caricheranno fisicamente la pagina e verificheranno la presenza degli elementi grafici.

---

## Risoluzione Problemi

### Tabella non visibile?
- Verifica che il modello sia attivo
- Controlla che la tabella sia stata generata

### Errore in campo relazione?
- Verifica che il modello target esista
- Controlla i permessi sul modello target

---

*Documento aggiornato: Febbraio 2026*
