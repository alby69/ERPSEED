# Visione del Progetto ERP Modulare

## Obiettivo

Il progetto ha l'obiettivo di creare un sistema ERP modulare e flessibile, basato su un'architettura a "mattoncini" (Lego) che permette di costruire, estendere e aggiornare i moduli senza compromettere la funzionalità complessiva.

---

## Architettura del Sistema

### Tabelle Generiche (Archetipi)

#### 1. Soggetto
Tabella centrale contenente le informazioni anagrafiche generiche:
- Dati anagrafici di base
- Relazione 1 a N con la tabella Ruolo

#### 2. Ruolo
Tabella per definire i ruoli associati a un soggetto:
- Cliente
- Fornitore
- Autista
- Dipendente
- Consulente
- Spedizioniere
- (altri ruoli personalizzabili)

#### 3. Indirizzo
Tabella per le informazioni geografiche:
- Via, città, CAP, provincia, stato
- Longitudine e Latitudine
- Collegabile a qualsiasi entità che necessiti di un indirizzo

#### 4. Testata e Riga
Archetipo per gestire documenti complessi:
- Testata: informazioni header del documento
- Riga: voci dettagliate collegate alla testata
- Esempi: Ordine Acquisto, Fattura, Ordine Vendita, ecc.

---

## Concetto di Modularità

### Mattoncini (Micro-servizi/Moduli)
- Piccole unità funzionali mappate in tabelle database
- Funzionalità CRUD di base
- Micro API propria per ogni modulo
- Agganciabili tra loro per formare componenti più grandi

### Container
- Gruppo di moduli collegati
- API unificate verso altri container
- Realizzano funzioni specifiche (moduli ERP)

### Robot (Moduli ERP completi)
- Container uniti che realizzano funzionalità complete
- Possibilità di aggiornamento e estensione
- Sostituzione di singoli mattoncini senza compromettere il container

---

## Builder (Generatore di Moduli)

Il Builder è una componente fondamentale che permette di:
1. Ricevere **template** contenenti:
   - Descrizione delle tabelle
   - Definizione dei campi
   - Relazioni tra tabelle
   - Procedure per la logica di funzionamento
2. Generare **automaticamente** un nuovo Modulo pronto all'uso
3. Integrare il modulo generato nel sistema ERP

---

## Vantaggi dell'Architettura

- **Flessibilità**: possibilità di aggiungere/rimuovere moduli
- **Scalabilità**: ogni componente può crescere indipendentemente
- **Manutenibilità**: sostituzione di componenti senza impattare il sistema
- **Estensibilità**: nuove funzionalità可以通过 nuovi moduli
- **Dynamicità**: possibilità di rendere le interfacce API dinamiche per funzionalità aggiuntive

---

## Approccio Bottom-up

Il sistema viene sviluppato partendo dai componenti base (mattoncini) per costruire funzionalità più complesse, garantendo solidità e modularità throughout l'intero sistema ERP.
