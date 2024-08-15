import azure.functions as func
import logging
import pyodbc
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="nbsazfunc1")
def nbsazfunc1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')

    if name:
        try: 
            key_vault_url = "https://nbskvailab.vault.azure.net"
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=key_vault_url, credential= credential)
            sqlusername = client.get_secret("nbssqlusr").value
            sqlpassword = client.get_secret("nbssqlusrpwd").value      

        except:
            logging.info("exception caught attempting to get secrets from AKV")
            return func.HttpResponse("exception caught attempting getting secrets from AKV", status_code = 500)
            
        #connect to SQL DB
        server = 'nbssqlsvr01.database.windows.net'
        database = 'nbs_sql_az1'
        driver = '{ODBC Driver 17 for SQL Server}'

        #retstr = sqlusername + ' ' + sqlpassword
        #return func.HttpResponse(retstr,  status_code = 500)

        try: 
            #conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+sqlusername +';PWD=' + sqlpassword) 
            # https://stackoverflow.com/questions/61628762/cant-open-lib-odbc-driver-17-for-sql-server-in-python
            conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=nbssqlsvr01.database.windows.net;PORT=1433;DATABASE=nbs_sql_az1;UID=nbssqlusr;PWD=nbssqlusr") 

        except pyodbc.Error as ex:
            logging.info("exception caught attemting to connect to SQL DB")
            logging.info(ex)
            return func.HttpResponse("exception caught attempting to connect to SQL DB", status_code = 500)


        # executing SQL query 
        allrecordsquery = "select * from inventory"
        car_models = []

        try:
            with conn.cursor() as cursor:
                cursor.execute(allrecordsquery)
                row = cursor.fetchall()

                for row in rows:
                    logging.info(row)
                    car_models.append(row[2]) 

            return func.HttpResponse({car_models})
        except pyodbc.Error as ex:
            logging.info("exceptioncaught attemting to execute SQL query")
            logging.info(ex)
            return func.HttpResponse("exception caught attempting to execute SQL query", status_code = 500)    
    else:
        return func.HttpResponse("Function triggered correctly", status_code=200)