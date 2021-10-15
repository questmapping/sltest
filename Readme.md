# Considerazioni
Non essendo presente un sistema di ACL per Streamlit e mettendo i dati su Repo pubblica, se si usano servizi come GCP Run è meglio evitare connessioni SQL e puntare tutto su Json, APi e Csv.

Utilizzando invece il servizion streamlit share è possibile posizionare in files sicuri le nostre chiavi di accesso: https://www.notion.so/Secrets-Management-730c82af2fc048d383d668c4049fb9bf
In questo caso, utilizzando il servizio di PythonAnywhere, è stato necessario collegarsi al DB tramite tunnel SSH https://help.pythonanywhere.com/pages/AccessingMySQLFromOutsidePythonAnywhere/

# Build and deploy

Command to build the application. PLease remeber to change the project name and application name
```
gcloud builds submit --tag gcr.io/<ProjectName>/<AppName>  --project=<ProjectName>
```

Command to deploy the application
```
gcloud run deploy --image gcr.io/<ProjectName>/<AppName> --platform managed  --project=<ProjectName> --allow-unauthenticated