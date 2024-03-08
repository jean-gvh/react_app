from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import PokemonSet, EbaySalesData
from collections import defaultdict


# Configuration de l'application Flask
app = Flask(__name__, '/static')

# Configuration de la base de données
DB_USER = 'root'
DB_PASSWORD = 'Tictact0c'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'test'

# Créez une connexion à la base de données MySQL
engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Session = sessionmaker(bind=engine)

app = Flask(__name__,static_folder='frontend/build/static')

@app.route('/api/getSalesData', methods=['GET'])
def get_sales_data():
    # Récupérez le nom du Pokémon à partir des paramètres de requête
    pokemon_name = request.args.get('pokemon_name')

    # Effectuez les opérations nécessaires pour obtenir les données de ventes
    session = Session()
    pokemon_sales = session.query(EbaySalesData).options(joinedload('pokemon_set')).filter(EbaySalesData.card_name == pokemon_name).all()

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

if __name__ == '__main__':
    app.run(debug=True)