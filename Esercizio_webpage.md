# Esercizio: Creazione di un Sito Web con Copilot e Modelli di Reasoning

## Obiettivo

Questo esercizio ha come scopo la realizzazione incrementale di un sito web dedicato alle recensioni di prodotti tecnologici, utilizzando **GitHub Copilot** con il modello **Claude 3.7 Sonnet Thinking**.

Il sito verrà sviluppato attraverso una serie di **task progressivi**, ciascuno dei quali aggiunge funzionalità o migliora l’implementazione esistente. Alcuni task richiederanno anche la correzione di bug presenti nei passaggi precedenti.

---

## Struttura del progetto

All’interno della cartella `Esercizio_webpage` sono presenti diverse sottocartelle, ciascuna corrispondente a uno **step** dell’esercizio:

- La cartella `Base` contiene una versione minimale del sito web, con funzionalità essenziali.
- Le cartelle `step_1`, `step_2`, ..., `step_6` rappresentano le soluzioni complete per ciascun task. Ogni step mostra come dovrebbe essere il sito al termine di quella fase di sviluppo.

Il lavoro consiste nel partire dal codice della cartella `Base` e, tramite l’interazione con Copilot, **aggiungere progressivamente le funzionalità richieste**, fino ad arrivare alla versione finale del sito, contenuta nella cartella `step_6`.

---

## Uso di Copilot

Durante l’esercizio si consiglia di utilizzare entrambe le modalità disponibili in GitHub Copilot:

- **Ask**
- **Edit**

L’uso dell’una o dell’altra modalità dipende dal tipo di modifica da apportare e da come si desidera procedere.

Per ottenere risultati ottimali, è fondamentale **fornire sempre a Copilot il contesto corretto**, cliccando sul pulsante **"Add Context..."** e selezionando i file rilevanti per il task che si sta affrontando (si ricordi che è possibile fornire l'intera cartella di progetto per task che richiedono l'orchestrazione di molti file).

---

## Dettagli tecnici e Avvio dell’applicazione

Il sito è sviluppato utilizzando il framework **FastAPI** e utilizza **SQLite** come sistema di database.  
L’interazione con il database avviene tramite **SQLAlchemy**, usato come ORM (Object-Relational Mapper).

Il file del database è chiamato `reviews.db` e si trova nella **directory principale del progetto**.

Per visualizzare il sito in esecuzione, è necessario **avviare il server locale**.  
Aprire un terminale, **navigare all’interno della cartella dello step su cui si sta lavorando** (ad esempio `Base`, `step_1`, ecc.) ed eseguire il comando:

```bash
python run.py
```
Questo avvierà il server FastAPI e renderà il sito accessibile da browser all’indirizzo `http://127.0.0.1:8000`.


## Descrizione della versione base e dei task successivi

Nei prossimi paragrafi verranno descritte:

- Le funzionalità presenti nella versione iniziale del sito (`Base`)
- I 6 task da completare per arrivare progressivamente al risultato finale (`step_6`)

---

## Funzionalità della versione base del sito

La versione iniziale del sito web presenta una struttura completa con alcune funzionalità di base già operative. Di seguito vengono elencate le caratteristiche implementate:

### Architettura generale

- Il sito è composto da quattro pagine principali:
  - **Home page**
  - Pagina **Smartphone**
  - Pagina **Computer**
  - Pagina **Audio**

- Ogni pagina di categoria mostra i prodotti con le relative recensioni associate.

- Dalla pagina di un singolo prodotto è possibile:
  - Scrivere una recensione con un **punteggio da 1 a 5 stelle** specificando un nome autore.
  - Ordinare le recensioni secondo quattro criteri:
    - Data di pubblicazione (crescente o decrescente)
    - Numero di stelle (crescente o decrescente)

### Descrizione della Home page

- Visualizza le **ultime 12 recensioni** pubblicate nella sezione **Recensioni in evidenza**.
- Mostra il pulsante **“Leggi le recensioni”** che al clic effettua uno scroll verso il basso fino alla sezione **Recensioni in evidenza**.
- Contiene una sezione dedicata all’iscrizione alla **newsletter**:
  - Il pulsante di iscrizione è **presente ma non è implementata alcune funzionalità dietro ad esso**.
- Presenta pulsanti di collegamento ai **social**, anch'essi **non funzionanti** (e lo rimarranno anche nelle versioni successive).
- Sono presenti pulsanti di navigazione (sia in alto che in basso) per accedere rapidamente alle tre pagine di categoria: Smartphone, Computer e Audio.

### Presenza di Bug

- È presente un **bug nella gestione delle recensioni**:
  - Quando si scrive una recensione dalla pagina del prodotto *X* e si cambia il nome del prodotto in *Y*, la recensione viene comunque **associata e visualizzata nella pagina di *X***, invece che in quella corretta (*Y*).

---

## Step 1 — Aggiunta della funzionalità di profilo utente

A partire dalla versione `Base`, il primo task consiste nell’aggiunta delle funzionalità relative alla gestione dell’utente. L’obiettivo è permettere la registrazione, l’accesso e la visualizzazione di un profilo personale.

### Funzionalità da implementare

- **Accesso e registrazione**
  - Nella homepage devono essere visibili due nuovi pulsanti: **“Accedi”** e **“Registrati”**, che rimandano alle rispettive pagine.
  - La pagina di **registrazione** deve prevedere l’inserimento di:
    - Username  
    - Email  
    - Password  
    - Conferma della password  
  - Durante la registrazione:
    - Devono essere imposti dei **requisiti minimi di sicurezza** per la password.
    - I requisiti devono essere esplicitamente indicati e deve esserci un modo per mostrare graficamente (es. check visivi) quando tutti i requisiti sono stati soddisfatti.
  - La pagina di **login** deve richiedere:
    - Email  
    - Password  
    - Un pulsante **“Password dimenticata?”**, che **non** ha per il momento alcune funzionalità implementata.

- **Stato dell’utente**
  - Dopo aver effettuato il login, l’utente deve:
    - Vedere chiaramente di essere autenticato.
    - Poter accedere al proprio **profilo personale** tramite un pulsante dedicato.

- **Pagina del profilo**
  - Deve essere una pagina separata con due sezioni:
    - **Informazioni account**: mostra username, email e data di iscrizione.
    - **Le mie recensioni**: sezione attualmente **vuota**, da completare nei task successivi.
  - Devono essere presenti due pulsanti:
    - **Logout**, con funzionalità già attiva. Una volta effettuata la disconnessione, l’interfaccia della homepage torna a mostrare i pulsanti **“Accedi”** e **“Registrati”** al posto di quello per il profilo.
    - **Modifica profilo**, ancora **non funzionante**.

### Funzionalità ancora incomplete

- Il pulsante **“Modifica profilo”** è presente ma non ancora operativo.
- Il pulsante **“Password dimenticata?”** non ha alcuna azione associata.
- La sezione **“Le mie recensioni”** risulta ancora vuota.

Tutte le altre funzionalità del sito rimangono **inalterate** rispetto alla versione `Base`.

---

## Step 2 – Funzionalità di Recupero Password

In questo step si estende la gestione dell’autenticazione implementando la funzionalità legata al pulsante **"Password dimenticata?"**.

### Funzionalità da implementare

- Il pulsante **"Password dimenticata?"** deve ora essere collegato a una nuova pagina dedicata al reset della password.
- In questa pagina l’utente può inserire il proprio indirizzo email per ricevere un link di ripristino.
- Il sito deve essere in grado di **inviare un’email** all’indirizzo specificato contenente il link per reimpostare la password.
- Il link deve portare ad una nuova pagina dedicata in cui sono presenti i campi:
  - **Nuova password**
  - **Conferma password**
- La nuova password deve rispettare gli stessi **requisiti minimi di sicurezza** già previsti in fase di registrazione.
  - I requisiti devono essere **chiaramente esplicitati** nella pagina
  - Deve essere presente un **feedback grafico** che segnali quando **tutti** i requisiti sono stati soddisfatti
- Nella pagina di reimpostazione della password deve essere presente un bottone **"Reimposta password"** che, una volta premuto, deve:
  - Aggiornare la password nel database.
  - Reindirizzare l’utente alla pagina di login.

### Gestione dell'invio email

Il sistema di invio email deve essere regolato tramite una variabile `DEBUG_MODE`:

- Se `DEBUG_MODE = True`, il contenuto delle email viene **stampato a terminale** (per uso in fase di sviluppo).
- Se `DEBUG_MODE = False`, le email vengono **realmente inviate**.

### Dati di configurazione

Per l'invio delle email reali (con `DEBUG_MODE = False`), l'applicazione deve essere configurata con le seguenti credenziali di accesso per il server email:

- EMAIL_HOST: "smtp.gmail.com"
- EMAIL_PORT: 587
- EMAIL_USERNAME: "workshopreasoningmodels@gmail.com"
- EMAIL_PASSWORD: "************"

Tutte le altre funzionalità del sito rimangono **inalterate** rispetto allo step precedente (`step_1`).

---

## Step 3 – Modifica dell’Email e della Password

In questo step si aggiungono funzionalità al profilo utente, implementando le azioni collegate al pulsante **“Modifica profilo”**.

### Funzionalità da implementare

Cliccando su **“Modifica profilo”**, l’utente deve essere reindirizzato a una nuova pagina dedicata alla modifica delle **credenziali di accesso**.  
La pagina deve essere suddivisa in due sezioni distinte.

#### Sezione "Cambia Email"

Questa sezione deve permettere all’utente di aggiornare il proprio indirizzo email, mostrando:

- **Email attuale** (precompilata e non modificabile)
- **Nuova email**
- **Password** (per confermare l’operazione in modo sicuro)

Azioni disponibili:

- Pulsante **“Aggiorna Email”** per confermare la modifica
- Pulsante **“Annulla”** per annullare l’operazione e tornare alla pagina del profilo

#### Sezione "Cambia Password"

Questa sezione deve permettere all’utente di aggiornare la propria password, mostrando:

- **Password attuale** (per confermare l’operazione in modo sicuro)
- **Nuova password**
- **Conferma password**

La nuova password deve rispettare gli stessi **requisiti minimi di sicurezza** già previsti in fase di registrazione.

- I requisiti devono essere **chiaramente esplicitati** nella pagina
- Deve essere presente un **feedback grafico** che segnali quando **tutti** i requisiti sono stati soddisfatti

Azioni disponibili:

- Pulsante **“Aggiorna Password”** per confermare la modifica
- Pulsante **“Annulla”** per annullare l’operazione e tornare alla pagina del profilo

Tutte le altre funzionalità del sito rimangono **inalterate** rispetto allo step precedente (`step_2`).

---

## Step 4 – Miglioramento della gestione delle recensioni e correzione del bug

In questo step si interviene sul sistema di recensioni, con l’obiettivo di migliorarne l’usabilità, la coerenza e correggere il bug presente sin dalla versione iniziale del sito.

### Funzionalità da implementare

- **Accesso richiesto per scrivere una recensione**
  - Il pulsante all’interno della pagina di un prodotto deve cambiare comportamento in base allo stato dell’utente:
    - Se **non loggato**, il pulsante deve riportare la scritta **“Accedi per scrivere una recensione”** e deve reindirizzare alla pagina di login.
    - Se **loggato**, il pulsante deve riportare la scritta **“Scrivi una recensione”** e deve reindirizzare a una **pagina dedicata** all’inserimento della recensione (non più un form nella stessa pagina).

- **Pagina dedicata alla creazione di una recensione**
  - Deve contenere i seguenti campi:
    - **Titolo** (campo testuale)
    - **Descrizione** (campo testuale)
    - **Nome Prodotto** (campo testuale)
    - **Categoria** (menu a tendina con opzioni: Seleziona una categoria, Smartphone, Computer, Audio)
    - **Valutazione**, selezionabile attraverso un sistema di 5 stelle interattive (da 1 a 5)
  - I campi **Nome Prodotto** e **Categoria** devono essere **precompilati automaticamente** in base al prodotto visualizzato quando si è cliccato il pulsante **“Scrivi una recensione”**.
  - Devono essere presenti due pulsanti:
    - **“Annulla”**, che riporta alla homepage
    - **“Invia Recensione”**, che salva la recensione
  - Quando l'utente clicca sul pulsante **Invia Recensione**, deve essere effettuato un controllo per assicurarsi che tutti i campi siano stati compilati prima di inviare la recensione.

- **Eliminazione del bug**
  - Quando si crea una recensione partendo dalla pagina del prodotto *X*, ma si modifica manualmente il campo **Nome Prodotto** impostandolo su *Y*, la recensione deve essere **correttamente associata e visualizzata nella pagina del prodotto *Y***, e **non** in quella del prodotto *X*.

- **Attribuzione automatica dell’autore**
  - Il nome dell’utente **non deve più essere richiesto**: ogni recensione deve risultare firmata automaticamente con lo username dell’utente loggato.

- **Pulsante “Scrivi una recensione” nella homepage**
  - A fianco del pulsante **“Leggi le recensioni”**, nella homepage deve comparire:
    - Se **non loggati**: il pulsante **“Accedi per scrivere una recensione”** che rimanda alla pagina di login.
    - Se **loggati**: il pulsante **“Scrivi una recensione”** che rimanda alla pagina di creazione di una recensione.
  - In questo caso, il campo **Nome Prodotto** non deve essere precompilato mentre il campo **Categoria** deve essere preimpostato sull’opzione **“Seleziona una categoria”**.

Tutte le altre funzionalità del sito rimangono **inalterate** rispetto allo step precedente (`step_3`).
---

## Step 5 – Gestione delle recensioni personali

In questo step viene attivata la sezione **“Le mie recensioni”** nella pagina del profilo utente. L’obiettivo è permettere all’utente di visualizzare, modificare ed eliminare le recensioni da lui pubblicate.

### Funzionalità da implementare

- **Visualizzazione delle recensioni personali**
  - Nella sezione **“Le mie recensioni”** devono essere visualizzate **tutte le recensioni** scritte dall’utente loggato.
  - Ogni recensione deve presentare tre pulsanti:
    - **“Vedi”** (azzurro): reindirizza alla pagina del prodotto, posizionando la visualizzazione **esattamente in corrispondenza della recensione**, non all’inizio della pagina.
    - **“Modifica”** (arancione): apre una pagina per modificare la recensione esistente.
    - **“Elimina”** (rosso): elimina definitivamente la recensione.

- **Modifica della recensione**
  - La pagina di modifica deve contenere solo i seguenti campi:
    - **Titolo**  
    - **Descrizione**  
    - **Valutazione** (stelle da 1 a 5)  
  - I campi devono essere **precompilati** con i dati della recensione originale.
  - Devono essere presenti due pulsanti:
    - **“Annulla”** che riporta alla pagina del profilo.
    - **“Aggiorna recensione”** che salva la nuova versione della recensione, **sostituendo** quella precedente.

- **Eliminazione della recensione**
  - Al clic del pulsante **“Elimina”**, deve comparire un **popup di conferma** per evitare cancellazioni accidentali.
  - Se, a seguito dell’eliminazione di una recensione, un prodotto risulta **privo di recensioni**, esso deve essere **rimosso automaticamente dalla bacheca dei prodotti** della categoria corrispondente.

Tutte le altre funzionalità del sito rimangono **inalterate** rispetto allo step precedente (`step_4`).

---

## Step 6 – Funzionalità della Newsletter

In questo step viene introdotta una nuova funzionalità: la **newsletter**, indipendente dal sistema di registrazione utente.

### Funzionalità da implementare

- L’iscrizione alla newsletter si effettua inserendo un indirizzo email nella sezione dedicata e confermando con il pulsante **“Iscriviti”**.
- La newsletter è **indipendente** dal profilo utente:
  - Un utente può essere iscritto alla newsletter **senza avere un profilo**.
  - Un utente registrato può **non essere iscritto** alla newsletter.
- Dopo aver cliccato su **“Iscriviti”**:
  - Se l’indirizzo email **non era già iscritto**, l’iscrizione deve avvenire correttamente e deve essere mostrato un **banner di conferma**.
  - Se l’indirizzo era **già iscritto**, deve comparire un **banner informativo** che avvisa della situazione.
  - Nel primo caso deve essere **inviata un’email** di notifica dell'avvenuta iscrizione all’indirizzo specificato.

### Notifiche per nuove recensioni

- Ogni volta che viene **aggiunta una nuova recensione**, tutte le persone iscritte alla newsletter devono ricevere una **mail di notifica** contenente:
  - Il **testo completo della recensione**.
  - Un pulsante con la scritta **“Visualizza la recensione sul nostro sito”** che rimanda direttamente alla pagina del prodotto a cui appartiene la recensione.

### Disiscrizione dalla newsletter

- Tutte le email inviate (sia quella di conferma iscrizione che quelle di notifica di una nuova recensione pubblicata) devono contenere in fondo un **link per disiscriversi**.
- Una volta effettuata la disiscrizione, **non devono più essere inviate email** a quell’indirizzo quando una nuova recensione viene pubblicata.

### Gestione dell’invio email

L’invio delle email deve utilizzare lo stesso sistema definito nello `step_2`:

- Il comportamento è regolato dalla variabile `DEBUG_MODE`:
  - Se `DEBUG_MODE = True`, il contenuto delle email viene stampato a terminale.
  - Se `DEBUG_MODE = False`, le email vengono inviate realmente.

Tutte le altre funzionalità del sito rimangono **inalterate** rispetto allo step precedente (`step_5`).


