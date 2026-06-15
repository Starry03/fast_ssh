# fast_ssh

CLI per gestire host SSH con password memorizzate in modo cifrato.

## Flusso

1. Avvia il programma.
2. Inserisci la master password per sbloccare il database.
3. Seleziona il nome host da connettere.
4. `fast_ssh` apre la sessione SSH e inserisce automaticamente la password dell'host quando viene richiesta.

## Note

- Le password degli host restano cifrate nel database e vengono decrittate solo dopo lo sblocco.
- La connessione usa una sessione SSH interattiva, quindi dopo il login puoi usare il terminale normalmente.
