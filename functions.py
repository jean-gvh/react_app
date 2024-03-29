import os
from google.cloud import storage
import csv
import json

from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from flask import jsonify

def get_pokemon_names():

    # Charger le contenu JSON
    json_content = {
        "type": "service_account",
        "project_id": "ppt1-414709",
        "private_key_id": "b9173683cc79e1a5d0a9114fd00f4cd9c2528ed5",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCnI5CLzsRYjGt8\nNq/EkDU2wkH2MdiLRAKBmaR+h9cus7gl7KKFpzFN8pPxTElot1GhxLgCxaY2ZsTR\n4VxBOAdnnHckznRnIvkNy6eVwO0kgYGufYuKxfc3pEL+2jnqs7GDf47LTPjCTZyn\nf2CKPnib9zUnJtWeCAhsTyUkS5k86/E4GNA3U/cGx9+ikSrB5g6ac8TAQUVSVZF4\ncE05yqkM4TGgCV0yvrpizYO73w5/veEN8gDH3g4m8tsF5nVKI+f/jR+JUesYrJZy\n+4+lUBoztzYFEp3wds6SkCM1wMZV+TOTkEju+cmrapDLue3TiyohbQyCIAuHOZhw\nesLlqFRxAgMBAAECggEAEH1/y2txD9N631x95wTbWzW7UFEGrmbdYHAKPLmmT2NH\n7eX0+v7N7ITcd9gw/fXoRe+kwBFEHuXw0UxMz9p5UI2ta6I69doLfIL1W98XBp0I\ncHDOjbiOdZztRzu8rx1fjDvPmNtVR8ZkiFoW6kzTlX/EbMJ2HQtp2VXNslELI2lz\nI+5/2VPjUsLmlOBS1STmyJFcM73fkeMoH73SqizqyXmX/u1YcxlyZ7aKvYA3jSCv\n4cHDJ1y6Y+Y72rDJPbqQQ2kWjuktGGjcSdkZjrC+mPsH0Mb+bkYByzB0IECosmmB\niPMOQYFH9d/xNNesA/yQbu+1KMT7RirfkxDctO8Y4QKBgQDUsSLE9c23hJu2M2B8\n2sCHmYsUlo03tcjV4AXwFZJ3Xf6ofV2muB9pTb/CaYtS0zIex/aNiZBBsc4ouN2d\nUzMaphQM/myWkJHroQSYMAuzDaVGGxZGPCIuUKh8HD1NIxfcFzffFRjE2Vjv006p\nmvp1oRrt5Mu34y4jddCX1wMCFQKBgQDJK+oYkMwkKhyWt16eAhRY8JdqW9LNuFB5\nSIWB9jsBrrYifjudH2g5hNK+3X5fDitujxUmEv7IjYHTcTIuGIWq05l1riSY9miO\nXYKXLek2OWfR1PhV6YZFd0PFKVG1ajiu4t1QkcLfARuQJwX0+My1oS0jG/AocLpi\nIsseFEaL7QKBgQCrWjY31gwxQK2uQYAHtrkLxeDt6kjFTDgMTtqZzNdeQaTLm4ya\np5Xu4YuPFjb/uFSVxeXVq7FDq/r6hc1NVV1Dp+9ZdJSJTNmyqtunvHWAgIrZizML\nzKCBDcxfiOS+Q3qSf0Ys/LMizDRBqsyiCdCkefHXHNAfSvC98snlunya7QKBgQCZ\nMaLkMCf1BkidEWixJN4/2H9F1EUUud42bd6VWGAY6OX0IHLfNRKWcqpWBK/+TPkQ\nCU/Onbp+GRybWuEerzfjHZ4IOqPOBB8dAuK2o5Sr4U1JQkgWjG3eqnLmSo/ZedlO\nfJ6Sg12Fmv9VaBImOe0SB3oq+VSKR0X4A4zwC/qpBQKBgQDDpKIzOmoMZ+7zywfv\neeHVk1+TcO43AQtf/2KxtiyX2tCBdggyCZzRSB2H7V6p/x4vEqPgb3ONPEQgyL2X\nmiBZyvcdQ9YEWZkgs1RNOveixQCHjYROxDFZRL1ewHWFWsOEYfu6/fjuEhUHygw9\ni9cHPJ+cflNxaKF0LCzpTniIMQ==\n-----END PRIVATE KEY-----\n",
        "client_email": "master@ppt1-414709.iam.gserviceaccount.com",
        "client_id": "111116894633701816817",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/master%40ppt1-414709.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    # Enregistrer le contenu JSON dans un fichier temporaire
    with open("temp_credentials.json", "w") as json_file:
        json.dump(json_content, json_file)

    # Utiliser le contenu du fichier JSON pour accéder aux services GCP
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "temp_credentials.json"

    # Exemple d'utilisation du client Google Cloud Storage
    storage_client = storage.Client()
    
    

    # Remplacez 'your-bucket-name' par le nom de votre bucket GCS et 'pokemon_names.csv' par le chemin vers votre fichier CSV
    bucket_name = 'ppt1-base-data'
    blob_name = 'app_research_pokemon/app_research_pokemon.csv'


    # Accéder au bucket et récupérer le blob
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Télécharger le contenu du fichier CSV en mémoire
    csv_content = blob.download_as_string() 

    return csv_content 

def get_pokemon_suggestions(term):
    suggestions = []

    csv_content = get_pokemon_names()

    # Lire le contenu CSV et obtenir les suggestions de noms de Pokémon
    csv_data = csv_content.decode('utf-8').splitlines()
    reader = csv.DictReader(csv_data)
    for row in reader:
        if term.lower() in row['card_name'].lower():
            suggestions.append({
                'card_name': row['card_name'],
                'img_link': row['img_link'],
                'set_name': row['set_name'],
                'bloc_name': row['bloc_name']
            })
    suggestions = suggestions[:6]
    return suggestions 



#eBay Auctions API Call

def get_auctions_results(parameters):
    APPLICATION_ID='jeanguin-test-PRD-321e8fc30-d70f07ea'
    try:
        api = Finding(domain='svcs.ebay.fr', appid=APPLICATION_ID, config_file=None, siteid='EBAY-FR')
        parameters['itemFilter'] = [
            {'name': 'LocatedIn', 'value': 'FR'},
            {'name': 'ListingType', 'value': 'Auction'}
        ]
        response = api.execute('findItemsAdvanced', parameters)
        return response.dict()
    except ConnectionError as e:
        print(e)
        print(e.response.dict()) 




def extract_info(response):
    items = response.get('searchResult', {}).get('item', [])
    extracted_info = []

    for item in items:
        item_info = {
            'title': item.get('title', ''),
            'galleryURL': item.get('galleryURL', ''),
            'viewItemURL': item.get('viewItemURL', ''),
            'location': item.get('location', ''),
            'currentPrice': item.get('sellingStatus', {}).get('currentPrice', {}).get('value', ''),
            'currency': item.get('sellingStatus', {}).get('currentPrice', {}).get('_currencyId', ''),
            'bidCount': item.get('sellingStatus', {}).get('bidCount', ''),
            'sellingState': item.get('sellingStatus', {}).get('sellingState', ''),
            'startTime': item.get('listingInfo', {}).get('startTime', ''),
            'endTime': item.get('listingInfo', {}).get('endTime', ''),
            'watchCount': item.get('listingInfo', {}).get('watchCount', ''),
            'condition': item.get('condition', {}).get('conditionDisplayName', '')
        }
        extracted_info.append(item_info)

    return jsonify(extracted_info) 


#eBay Direct Offers API Call

def get_direct_offers_results(parameters):
    APPLICATION_ID='jeanguin-test-PRD-321e8fc30-d70f07ea'
    try:
        api = Finding(domain='svcs.ebay.fr', appid=APPLICATION_ID, config_file=None, siteid='EBAY-FR')
        parameters['itemFilter'] = [
            {'name': 'LocatedIn', 'value': 'FR'},
            {'name': 'ListingType', 'value': 'FixedPrice'}
        ]
        response = api.execute('findItemsAdvanced', parameters)
        return response.dict()
    except ConnectionError as e:
        print(e)
        print(e.response.dict()) 


def direct_offers_extract_info(response):
    items = response.get('searchResult', {}).get('item', [])
    extracted_info = []
    for item in items:
        item_info = {
            'title': item.get('title', ''),
            'startTime' : item.get('starttime',''),
            'galleryURL': item.get('galleryURL', ''),
            'viewItemURL': item.get('viewItemURL', ''),
            'location': item.get('location', ''),
            'currentPrice': item.get('sellingStatus', {}).get('currentPrice', {}).get('value', ''),
            'currency': item.get('sellingStatus', {}).get('currentPrice', {}).get('_currencyId', ''),
            'condition': item.get('condition', {}).get('conditionDisplayName', ''),
            'watchCount': item.get('listingInfo', {}).get('watchCount', ''),
            'shippingServiceCost': item.get('shippingInfo', {}).get('shippingServiceCost', {}).get('value', ''),
            'shippingServiceCurrency': item.get('shippingInfo', {}).get('shippingServiceCost', {}).get('_currencyId', '')
        }
        extracted_info.append(item_info)
    return jsonify(extracted_info)