# Amministrazione

## Introduzione

La sezione amministrazione permette di gestire: progetti, utenti, permessi, backup e sicurezza.

Vedi [03_MODULI.md](03_MODULI.md) per la gestione dei moduli (attivare/disattivare).

---

## Gestione Progetti

I progetti sono contenitori isolati con propri dati, utenti e configurazioni.

### Creare un Progetto

1. Accedi come amministratore
2. Vai su **Amministrazione → Progetti**
3. Clicca **Nuovo Progetto**
4. Compila:
   - **Nome**: Identificativo
   - **Descrizione**: Descrizione del progetto
   - **Template**: Vuoto, Base, Completo

### Template di Progetto

- **Vuoto**: Solo sistema
- **Base**: Anagrafica, Prodotti, Vendite base
- **Completo**: Tutti i moduli attivi

### Import/Export

**Export**:
1. Apri il progetto
2. **Impostazioni → Esporta**
3. Scarica file JSON

**Import**:
1. Crea nuovo progetto
2. **Impostazioni → Importa**
3. Carica JSON

---

## Gestione Utenti

### Creare Utenti

1. **Amministrazione → Utenti**
2. **Nuovo Utente**
3. Compila:
   - **Email**: Indirizzo univoco
   - **Nome**: Nome visualizzato
   - **Ruolo**: Admin, Editor, Viewer
   - **Progetto**: Appartenenza

### Assegnare Progetti

Un utente può appartenere a più progetti con ruoli diversi:

1. Apri scheda utente
2. **Progetti**
3. Aggiungi progetto e ruolo

### Reset Password

1. **Amministrazione → Utenti**
2. Seleziona utente
3. **Reset Password**
4. L'utente riceve email per nuova password

---

## Sistema di Permessi

### Livelli Globali

| Ruolo | Descrizione |
|-------|-------------|
| **Admin** | Accesso completo, gestisce utenti e configurazioni |
| **Editor** | Crea, modifica, elimina record |
| **Viewer** | Solo lettura |

### Permessi Specifici

Oltre al ruolo globale, permessi per singolo modulo/entità:

1. **Amministrazione → Permessi**
2. Seleziona modulo/entità
3. Definisci azioni per ruoli

### Permessi di Campo

Singoli campi con permessi specifici:

- **Visibile**: L'utente vede il campo
- **Editable**: L'utente modifica il campo
- **Hidden**: Campo non visibile

---

## Audit Log

Il sistema registra tutte le operazioni significative.

### Cosa viene registrato

- Creazione, modifica, eliminazione record
- Login e logout
- Modifiche configurazioni
- Operazioni admin

### Consultare l'Audit Log

1. **Amministrazione → Audit Log**
2. Filtra per:
   - Data
   - Utente
   - Modulo/Entità
   - Tipo operazione
3. Visualizza dettagli

### Esportazione

1. Seleziona periodo
2. **Esporta**
3. Scarica CSV o Excel

---

## Backup e Restore

### Backup Automatici

Configurabili in **Impostazioni → Backup**:

- Frequenza
- Numero backup da mantenere
- Destinazione (locale/cloud)

### Backup Manuale

1. **Amministrazione → Backup**
2. **Esegui Backup**
3. Scarica file

### Restore

1. **Amministrazione → Backup**
2. Seleziona backup
3. **Ripristina**
4. Conferma

**Attenzione**: Il restore sovrascrive i dati.

---

## Configurazione Tema

Personalizza l'aspetto per ogni progetto.

### Opzioni

- **Colore primario**
- **Modalità**: Chiaro/Scuro
- **Arrotondamento**
- **Logo**

### Configurare

1. Impostazioni progetto
2. **Tema**
3. Modifica opzioni
4. Salva

Le modifiche sono immediate.

---

## Sicurezza

### Policy Password

Configura:
- Lunghezza minima
- Obbligo maiuscole/minuscole/numeri
- Scadenza password
- Tentativi login massimi

### Sessioni

- Durata sessione
- Sessioni simultanee massime
- Timeout inattività

### Logout Remoto

1. **Amministrazione → Utenti**
2. Seleziona utente
3. **Termina Sessioni**

Tutte le sessioni vengono chiuse.

---

## Best Practices

### Sicurezza
- Usa password robuste
- Abilita verifica due passaggi
- Limita account admin
- Consulta regolarmente audit log

### Backup
- Verifica periodicamente i backup
- Testa restore su ambiente test
- Tieni copie in location diverse

### Permessi
- Assegna il minimo permesso necessario
- Usa ruoli invece di permessi individuali
- Rivedi periodicamente gli accessi

---

*Documento aggiornato: Febbraio 2026*
