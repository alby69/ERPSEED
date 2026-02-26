# Guida all'Amministrazione

## Introduzione

La sezione amministrazione di FlaskERP permette di gestire tutti gli aspetti relativi a utenti, progetti, permessi e sicurezza. Questa guida ti accompagna attraverso le funzionalità principali.

---

## Gestione Progetti

I progetti sono il contenitore principale in FlaskERP. Ogni progetto rappresenta un'unità di lavoro isolata con i propri dati, utenti e configurazioni.

### Creare un Nuovo Progetto

1. Accedi come amministratore
2. Vai su **Amministrazione → Progetti**
3. Clicca **Nuovo Progetto**
4. Compila i dettagli:
   - **Nome**: Nome identificativo
   - **Descrizione**: Descrizione del progetto
   - **Template**: Puoi partire da un progetto vuoto o da un template predefinito

### Template di Progetto

I template permettono di partire con una configurazione predefinita:

- **Vuoto**: Nessun dato, solo il sistema
- **Base**: Include Anagrafica, Prodotti, Vendite base
- **Completo**: Include tutti i moduli attivi

### Import/Export Progetti

Puoi esportare un intero progetto per duplicarlo o farne backup:

**Export**:
1. Apri il progetto
2. Vai su **Impostazioni → Esporta**
3. Scarica il file JSON con tutta la configurazione

**Import**:
1. Crea un nuovo progetto
2. Vai su **Impostazioni → Importa**
3. Carica il file JSON

Questa funzionalità è utilissima per:
- Creare ambienti di test da produzione
- Duplicare configurazioni per nuovi clienti
- Fare backup completi

---

## Gestione Utenti

### Creare Utenti

1. Vai su **Amministrazione → Utenti**
2. Clicca **Nuovo Utente**
3. Compila:
   - **Email**: Indirizzo univoco
   - **Nome**: Nome visualizzato
   - **Ruolo**: Admin, Editor, Viewer
   - **Progetto**: A quale progetto appartiene

### Assegnare Progetti

Un utente può appartenere a più progetti con ruoli diversi:

1. Apri la scheda utente
2. Vai su **Progetti**
3. Aggiungi il progetto e seleziona il ruolo

### Reset Password

Se un utente dimentica la password:

1. Vai su **Amministrazione → Utenti**
2. Seleziona l'utente
3. Clicca **Reset Password**
4. L'utente riceverà un'email per impostare una nuova password

---

## Sistema di Permessi

Il sistema di permessi di FlaskERP è granulare e può essere configurato a più livelli.

### Livelli Globali

| Ruolo | Descrizione |
|-------|-------------|
| **Admin** | Accesso completo a tutto, può gestire utenti e configurazioni |
| **Editor** | Può creare, modificare, eliminare record |
| **Viewer** | Solo lettura, nessuna modifica |

### Permessi Specifici

Oltre al ruolo globale, puoi definire permessi specifici per singoli moduli o entità:

1. Vai su **Amministrazione → Permessi**
2. Seleziona il modulo o l'entità
3. Definisci quali azioni sono permesse per quali ruoli

### Permessi di Campo

Puoi nascondere o rendere readonly singoli campi per specifici ruoli:

- **Visibile**: L'utente può vedere il campo
- **Editable**: L'utente può modificare il campo
- **Hidden**: Il campo non è visibile

---

## Audit Log

Il sistema tiene traccia di tutte le operazioni significative attraverso l'Audit Log.

### Cosa viene registrato

- Creazione, modifica, eliminazione di record
- Login e logout
- Modifiche a configurazioni
- Operazioni di amministrazione

### Consultare l'Audit Log

1. Vai su **Amministrazione → Audit Log**
2. Filtra per:
   - Data
   - Utente
   - Modulo/Entità
   - Tipo operazione

3. Visualizza i dettagli di ogni operazione, incluse le modifiche specifiche ai campi

### Esportazione

Puoi esportare l'audit log per进行分析 o per scopi di compliance:

1. Seleziona il periodo
2. Clicca **Esporta**
3. Scarica in formato CSV o Excel

---

## Backup e Restore

### Backup Automatici

FlaskERP esegue backup automatici configurabili. Vai su **Impostazioni → Backup** per configurare:

- Frequenza backup
- Numero di backup da mantenere
- Destinazione (locale o cloud)

### Backup Manuale

Per un backup immediato:

1. Vai su **Amministrazione → Backup**
2. Clicca **Esegui Backup**
3. Scarica il file

### Restore

Per ripristinare un backup:

1. Vai su **Amministrazione → Backup**
2. Seleziona il backup da ripristinare
3. Clicca **Ripristina**
4. Conferma l'operazione

**Attenzione**: Il restore sovrascrive i dati esistenti. Fai sempre un backup prima di ripristinare.

---

## Configurazione Tema

FlaskERP permette di personalizzare l'aspetto visibile per ogni progetto.

### Opzioni di Tema

- **Colore primario**: Il colore principale dell'interfaccia
- **Modalità**: Chiaro o scuro
- **Arrotondamento**: Stile degli angoli
- **Logo**: Logo personalizzato per il progetto

### Configurare il Tema

1. Apri le impostazioni del progetto
2. Vai su **Tema**
3. Modifica le opzioni
4. Salva

Le modifiche sono immediate per tutti gli utenti del progetto.

---

## Gestione Moduli

Dalla sezione moduli puoi controllare quali funzionalità sono disponibili nel tuo progetto.

### Attivare un Modulo

1. Vai su **Amministrazione → Moduli**
2. Trova il modulo che ti serve
3. Clicca **Attiva**

### Disattivare un Modulo

1. Vai su **Amministrazione → Moduli**
2. Trova il modulo
3. Clicca **Disattiva**

Il modulo viene disattivato e rimosso dal menu. I dati vengono conservati.

---

## Sicurezza

### Policy Password

Configura le policy per le password:

- Lunghezza minima
- Obbligo maiuscole, minuscole, numeri
- Scadenza password
- Numero massimo tentativi login

### Sessioni

Configura la gestione delle sessioni:

- Durata sessione
- Sessioni simultanee massime
- Timeout di inattività

### Logout Remoto

Se sospetti un accesso non autorizzato:

1. Vai su **Amministrazione → Utenti**
2. Seleziona l'utente
3. Clicca **Termina Sessioni**

Tutte le sessioni attive dell'utente vengono chiuse.

---

## Best Practices

### Sicurezza

- Usa password robuste e cambiale regolarmente
- Abilita la verifica in due passaggi se disponibile
- Limita gli account admin ai soli che ne hanno bisogno
- Consulta regolarmente l'audit log

### Backup

- Verifica periodicamente che i backup funzionino
- Testa il restore su un ambiente di test
- Tieni copie di backup in location diverse

### Permessi

- Assegna il minimo permesso necessario
- Usa ruoli invece di permessi individuali quando possibile
- Rivedi periodicamente gli accessi

---

*Documento aggiornato: Febbraio 2026*
