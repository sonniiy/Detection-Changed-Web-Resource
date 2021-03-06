import logging
import azure.functions as func
from azure.storage.table import TableService
import urllib
import hashlib
import json
import uuid
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    initialHash = None

    # Get url from header
    urlHeader = req.headers.get('url')

    # Get account_name and account_key from body
    body = req.get_body().decode('utf8').replace("'", '"')
    bodyJSON = json.loads(body)
    account_name = bodyJSON.get('account_name')
    account_key = bodyJSON.get('account_key')

    # Connection to table and read initial Hash
    table_service = TableService(account_name, account_key)
    
    # Get inital Hash from table
    # Search URL in table
    filterContent = "URL eq '{}'".format(urlHeader)
    initialHashRows = list(table_service.query_entities('Hashes', filter = filterContent))

    # Catch Request Exceptions
    try:
        requ = requests.get(url=urlHeader)
    except requests.exceptions.RequestException:
        return func.HttpResponse("Problem with URL or connection", status_code=209)

    # Test if URL is still active
    statusCode = requ.status_code

    # For status code 204, it is not possible to write something into the response body, therefor only the status code is returned
    if str(statusCode) == '404':
        return func.HttpResponse(status_code=204)

    # Sort Hashes, which fit to URL
    if len(initialHashRows) != 0:
        sortedHashes = sorted(initialHashRows, key = lambda i: i['Timestamp'], reverse = True) 
        initialHashLine = sortedHashes[0]
        initialHash = initialHashLine['Hash']
    
    if urlHeader and account_name and account_key:
        
        # Get Bytes behind URL
        try:
           fb = urllib.request.urlopen(urlHeader)
        except requests.exceptions.RequestException:
           return func.HttpResponse("Problem with URL or connection", status_code=209)
        
        htmlInBytes = fb.read()
        fb.close()

        # Apply hash function
        htmlHash = hashlib.md5(htmlInBytes)
        htmlHashString=htmlHash.hexdigest()

        # Save Hash in Table Storage
        newHash = {'PartitionKey': 'HashAGB', 'RowKey': str(uuid.uuid1()), 'Hash' : htmlHashString, 'URL': urlHeader}
        table_service.insert_entity('Hashes', newHash)

        # Compare the newly calculated Hash with inital Hash 
        # First time hash is applied on this url  
        if initialHash is None:
            return func.HttpResponse("First time URL has been tested", status_code=202)
        
        # Hash has changed 
        elif initialHash != htmlHashString:
            return func.HttpResponse("URL has changed", status_code=201)

        # Hash has not changed
        else:
            return func.HttpResponse("URL has not changed", status_code=200)
    
    else:
        return func.HttpResponse(
             "Please pass the required parameters in body and header: URL in header, Account Key and Account Name for storage in body",
             status_code=400
        )
