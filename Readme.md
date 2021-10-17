# Considerazioni
Non essendo presente un sistema di ACL per Streamlit e mettendo i dati su Repo pubblica, se si usano servizi come GCP Run è meglio evitare connessioni SQL e puntare tutto su Json, API e Csv.

Utilizzando invece il servizio streamlit share è possibile posizionare in files sicuri le nostre chiavi di accesso: https://www.notion.so/Secrets-Management-730c82af2fc048d383d668c4049fb9bf

# Database
Utilizzando il servizio Mysql di PythonAnywhere, è stato necessario collegarsi al DB tramite tunnel SSH https://help.pythonanywhere.com/pages/AccessingMySQLFromOutsidePythonAnywhere/

Risulta quindi migliore la soluzione con DynamoDB di AWS

# Build and deploy on Streamlit Share
Basta registrarsi e seguire la procedura guidata. Per le chiavi di accesso di AWS basta inserire la sezione. Le chiavi è possibile crearle con la console di IAML

```
[aws_credentials]
aws_access_key_id = "XXXXXXXXXXXXXXXXXXXXX"
aws_secret_access_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
region_name = "eu-central-1"
```

In locale, questa parte va inserita nel file secrets.toml (ovviamente da inserire in .gitignore) come indicato da https://www.notion.so/Secrets-Management-730c82af2fc048d383d668c4049fb9bf


# Build and deploy on GC-RUN

Command to build the application. PLease remeber to change the project name and application name
```
gcloud builds submit --tag gcr.io/<ProjectName>/<AppName>  --project=<ProjectName>
```

Command to deploy the application
```
gcloud run deploy --image gcr.io/<ProjectName>/<AppName> --platform managed  --project=<ProjectName> --allow-unauthenticated