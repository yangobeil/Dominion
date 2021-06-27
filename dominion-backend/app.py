import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

load_dotenv()
username = os.getenv("mongo_username")
password = os.getenv("mongo_password")

app = Flask(__name__)
CORS(app)
host = f'mongodb+srv://{username}:{password}@recipes-3neas.mongodb.net/Dominion?retryWrites=true&w=majority'
client = MongoClient(host=host)
db = client.Dominion
collection = db.Cards
collection_combos = db.Combos


def get_extra_cards(cards, Fleau=None):
    card_names = [item['Card name'] for item in cards]
    extra_cards = []
    if Fleau:
        extra_cards.append({**collection.find_one({'Card name': Fleau}, {'_id': 0}), 'Type': 'Fléau'})
    if "Jeune sorcière" in card_names and not Fleau:
        out = list(collection.aggregate([{'$match': {'Card name': {'$nin': card_names},
                                                     'Expansion': 'Abondance',
                                                     'Can draft': True,
                                                     'Money cost': {'$in': [2, 3]}}},
                                         {'$sample': {'size': 1}}]))[0]
        out.pop('_id')
        extra_cards.append({**out, 'Type': 'Fléau'})
    if "Tournoi" in card_names:
        for prize in ["Diadème", "Fidèle destrier", "Partisans", "Princesse", "Sac d'or"]:
            extra_cards.append({**collection.find_one({'Card name': prize}, {'_id': 0}), 'Type': 'Prix'})
    if any(x in card_names for x in ["Maraudeur", "Cultiste", "Charrette de cadavres"]):
        for prize in ["Rescapés", "Ville en ruines", "Mine abandonnée", "Marché en ruines", "Bibliothèque en ruines"]:
            extra_cards.append({**collection.find_one({'Card name': prize}, {'_id': 0}), 'Type': 'Ruines'})
    if any(x in card_names for x in ["Camp de bandits", "Maraudeur", "Pillage"]):
        extra_cards.append({**collection.find_one({'Card name': 'Butin'}, {'_id': 0}), 'Type': ''})
    if 'Ermite' in card_names:
        extra_cards.append({**collection.find_one({'Card name': 'Fou'}, {'_id': 0}), 'Type': ''})
    if 'Orphelin' in card_names:
        extra_cards.append({**collection.find_one({'Card name': 'Mercenaire'}, {'_id': 0}), 'Type': ''})
    return extra_cards


@app.route('/random_cards', methods=['GET'])
def random_cards():
    extensions = request.args.getlist("extensions[]")
    distribution = request.args.get("distribution")
    if distribution:
        distribution = json.loads(distribution)
        card_list = []
        for ext in distribution.keys():
            card_list = card_list + list(collection.aggregate([{'$match': {'Expansion': {'$in': [ext]}, 'Can draft': True}},
                                                               {'$sample': {'size': distribution[ext]}}]))
    else:
        card_list = list(collection.aggregate([{'$match': {'Expansion': {'$in': extensions}, 'Can draft': True}},
                                               {'$sample': {'size': 10}}]))

    for card in card_list:
        card.pop('_id')
    card_list = card_list + get_extra_cards(card_list)
    return jsonify(card_list)


@app.route('/suggestions', methods=['GET'])
def suggestions():
    extensions = request.args.getlist("extensions[]")
    if len(extensions) == 1:
        combos = collection_combos.find({'Expansions': extensions})
    else:
        combos = collection_combos.find({'Expansions': {'$all': extensions}})
    suggestions = []
    for combo in combos:
        cards = [collection.find_one({'Card name': card}, {'_id': 0}) for card in combo['Cards']]
        sugg = {'Combo': combo['Combo'],
                'Cards': cards + get_extra_cards(cards, combo.get('Fleau'))}
        suggestions.append(sugg)
    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)