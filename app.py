from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import PokemonSet, EbaySalesData
from collections import defaultdict
from functions import get_auctions_results, get_direct_offers_results, extract_info, direct_offers_extract_info
from flask_pymongo import PyMongo
import bcrypt
from models import User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

# Configuration de l'application Flask
app = Flask(__name__,static_folder='frontend/build/static')
app.config["MONGO_URI"] = "mongodb://localhost:27017/user_test"
mongo = PyMongo(app)

# Configuration de la base de données
DB_USER = 'root'
DB_PASSWORD = 'Tictact0c'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'test2'

# Créez une connexion à la base de données MySQL
engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Session = sessionmaker(bind=engine)

app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète'
jwt = JWTManager(app)


@app.route('/api/getSalesData', methods=['GET'])
def get_sales_data():
    # Récupérez le nom du Pokémon à partir des paramètres de requête
    pokemon_name = request.args.get('pokemon_name')

    # Effectuez les opérations nécessaires pour obtenir les données de ventes
    session = Session()
    pokemon_sales = session.query(EbaySalesData).options(joinedload(EbaySalesData.pokemon_set)).filter(EbaySalesData.card_name == pokemon_name).all()

    # Prétraitement des dates et calculs
    grouped_data = defaultdict(lambda: {'prices': [], 'date': None})

    for sale in pokemon_sales:
        date_str = sale.sold_date.strftime('%Y-%m-%d')
        grouped_data[date_str]['prices'].append(sale.card_price_EUR)
        grouped_data[date_str]['date'] = date_str

    # Calcul des moyennes
    averaged_data = [{'date': group['date'], 'averagePrice': sum(group['prices']) / len(group['prices'])} for group in grouped_data.values()]

    # Trie des données par date
    averaged_data.sort(key=lambda x: x['date'])

    # Calcul des KPIs
    num_sales = len(pokemon_sales)
    avg_price = round(sum(sale.card_price_EUR for sale in pokemon_sales) / num_sales, 2) if num_sales > 0 else 0
    max_price = max(sale.card_price_EUR for sale in pokemon_sales) if num_sales > 0 else 0
    min_price = min(sale.card_price_EUR for sale in pokemon_sales) if num_sales > 0 else 0

    kpis = {'num_sales': num_sales, 'avg_price': avg_price, 'max_price': max_price, 'min_price': min_price}

    session.close()

    # Retournez les données au format JSON, y compris les données prétraitées
    return jsonify({
        'pokemon_name': pokemon_name,
        'sales': [{'card_name': sale.card_name, 'card_price_EUR': sale.card_price_EUR, 'sold_date': sale.sold_date, 'seller_ID': sale.seller_ID, 'pokemon_set': {'set_name': sale.pokemon_set.set_name}} for sale in pokemon_sales],
        'kpis': kpis,
        'chartData': averaged_data  # Ajoutez les données prétraitées ici
    })


@app.route('/search', methods=['GET'])
def search_ebay_auctions():
    payload = {
        'keywords': request.args.get('pokemon_name'),
        'paginationInput': {'entriesPerPage': 10}
    }

    #Requête à l'API pour obtenir les donnéess ur les enchères en cours 
    results = get_auctions_results(payload)

    #Filtrage des données retournées par la requête à l'API d'eBay
    extracted_info = extract_info(results)
   
    return extracted_info

@app.route('/search_directs_offers', methods=['GET'])
def search_ebay_direct_offers():
    parameters = {
        'keywords': request.args.get('pokemon_name'),
        'paginationInput': {'entriesPerPage': 10}
    }

    #Requête à l'API pour obtenir les donnéess ur les enchères en cours 
    results = get_direct_offers_results(parameters)

    #Filtrage des données retournées par la requête à l'API d'eBay
    direct_offers_extracted_data = direct_offers_extract_info(results)
   
    return direct_offers_extracted_data


# Route pour l'inscription
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    age = data.get('age')
    rgpd_consent = data.get('rgpd_consent')
    reason = data.get('reason')

    # Vérifier si l'utilisateur existe déjà
    user = mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]})
    if user:
        return jsonify({'error': 'Nom d\'utilisateur ou email déjà utilisé'}), 400

    # Créer un nouvel utilisateur
    new_user = User(username, password, email, age, rgpd_consent, reason)
    new_user.start_session(new_user)

    return jsonify({'message': 'Utilisateur créé avec succès'}), 201

# Route pour la connexion
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Vérifier si l'utilisateur existe
    user = mongo.db.users.find_one({'username': username})
    if not user:
        return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 400

    # Vérifier le mot de passe
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 400

    # Générer un token JWT
    access_token = create_access_token(identity=str(user['_id']))

    start_time = datetime.utcnow()

    # Ajouter la nouvelle session à l'utilisateur
    new_session = {
        'session_id': access_token,
        'start_time': start_time,
        'actions': []
    }
    mongo.db.users.update_one({'_id': user['_id']}, {'$push': {'sessions': new_session}})

    return jsonify({'token': access_token, 'user_id': str(user['_id'])}), 200



@app.route('/api/insertPokemonSearch', methods=['POST'])
@jwt_required()  # Assurez-vous que l'utilisateur est authentifié
def insert_pokemon_search():
    data = request.json
    # Récupérez l'identifiant de l'utilisateur à partir du token JWT
    user_id = get_jwt_identity()

    # Récupérez les données de la carte Pokémon à partir de la requête JSON
    pokemon_name = data.get('pokemon_name')
    image_url = data.get('image_url')
    set_name = data.get('set_name')
    bloc_name = data.get('bloc_name')

    # Insérez les données de la carte Pokémon dans la collection correspondante de MongoDB, en associant l'utilisateur et la session en cours
    mongo.db.user_searches.insert_one({
        'user_id': user_id,
        'pokemon_name': pokemon_name,
        'image_url': image_url,
        'set_name': str(set_name),
        'bloc_name': bloc_name
    })

    return jsonify({'message': 'Données de la carte Pokémon insérées avec succès'}), 200




if __name__ == '__main__':
    app.run(debug=True)