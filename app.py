import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import Flask, render_template, abort
import logging
import db

APP = Flask(__name__)

# Start Page
@APP.route('/')
def index():
    stats={}
    stats = db.execute('''
    SELECT COUNT(*) AS Houses FROM Houses;
    ''').fetchone()

    logging.info(stats)

    return render_template('index.html',stats=stats)

############ REGIÕES
@APP.route('/regions')
def regions():
    regions = db.execute(
        '''
        SELECT Region, Region_ID
        FROM Regions
        ORDER BY Region
        ''').fetchall()
    return render_template('regions.html', regions=regions)

@APP.route('/regions/<int:id>/')
def get_region(id):
    region = db.execute(
        '''
        SELECT Region_ID, Region, Description
        FROM Regions
        Where Region_ID = ?
        ''', [id]).fetchone()
    
    if region is None:
        abort(404, 'Region ID {} does not exist.'.format(id))

    ruller = db.execute(
        '''
        SELECT House_ID, House
        FROM Houses JOIN Regions 
        ON House_ID = Rulled_by_House_ID
        WHERE Region_ID = ?
        ''', [id]).fetchone()
    

    return render_template('regionsid.html', region=region, ruller=ruller)

######## Casas por região
@APP.route('/regions/<int:id>/houses')
def houses_by_region(id):
    houses = db.execute(
        '''
        SELECT House, House_ID, Words
        FROM Houses natural join Cities natural join Regions
        WHERE Region_ID=?
        ORDER BY House
        ''', [id]).fetchall()
    
    if not houses:
        abort(404, 'Region ID {} does not exist.'.format(id))

    qtd = db.execute(
        '''
        SELECT count(house_id) AS qtd
        FROM Houses natural join Cities natural join Regions
        WHERE Region_ID=?;
        ''', [id]).fetchone()
    return render_template('housesbyregion.html', houses=houses, qtd=qtd)

########## Cidades por região
@APP.route('/regions/<int:id>/cities')
def cities_by_region(id):
    cities = db.execute(
        '''
        SELECT city, region, city_id
        FROM cities NATURAL JOIN regions
        where region_ID = ?
        ORDER BY city
        ''', [id]).fetchall()
    
    qtd = db.execute(
        '''
        SELECT count(city_id) AS qtd
        FROM cities
        WHERE region_ID = ?
        ''', [id]).fetchone()
    
    return render_template('citiesbyregion.html', cities=cities, qtd=qtd)

########### Batalhas por região
@APP.route('/regions/<int:id>/battles')
def battles_by_region(id):
    battles = db.execute(
        '''
        SELECT battle_name, battle_ID, battle_type, year
        FROM battles
        WHERE region_ID = ?
        ORDER BY year, battle_name
        ''', [id]).fetchall()
    
    qtd = db.execute(
        '''
        SELECT count(battle_id) AS qtd
        FROM battles
        WHERE region_ID = ?
        ''', [id]
        ).fetchone()
    
    return render_template('battlesbyregion.html', battles=battles, qtd=qtd)

############ CASAS
@APP.route('/houses')
def houses():
    houses = db.execute(
        '''
        SELECT House, House_ID, Words
        FROM Houses
        ORDER BY House
        ''').fetchall()
    
    qtd = db.execute(
        '''
        SELECT count(house_id) AS qtd
        FROM houses;
        '''
        ).fetchone()
    return render_template('houses.html', houses=houses, qtd=qtd)

@APP.route('/houses/<int:id>/')
def get_house(id):
    house = db.execute(
        '''
        SELECT house_ID, house, Blazon_Description, blazon_url, city_id, city, region_id, region
        FROM houses natural join cities natural join regions
        Where house_ID = ?
        ''', [id]).fetchone()
    
    if house is None:
        abort(404, 'house ID {} does not exist.'.format(id))

    battles = db.execute(
        '''
        select battle_name, battle_ID, attackerhouse_id
        from battles natural join attacks
        where attackerhouse_id=?
        
        union 

        select battle_name, battle_ID, defenderhouse_id
        from battles natural join defenses
        where defenderhouse_id=?
        ''', [id, id]).fetchall()
    
    characters = db.execute(
        '''
        select character, character_ID
        from characters
        where house_ID=?
        ''', [id]).fetchall()
    

    return render_template('housesid.html', house=house, battles=battles, characters=characters)


############ BATALHAS
@APP.route('/battles')
def battles():
    battles = db.execute(
        '''
        SELECT battle_name, battle_ID, battle_type, year
        FROM battles
        ORDER BY year, battle_name
        ''').fetchall()
    
    qtd = db.execute(
        '''
        SELECT count(battle_id) AS qtd
        FROM battles;
        '''
        ).fetchone()
    
    return render_template('battles.html', battles=battles, qtd=qtd)

@APP.route('/battles/<int:id>/')
def get_battle(id):
    battle = db.execute(
        '''
        SELECT battle_id as id, battle_name as name, year, is_attacker_winner, battle_type as type, major_death, major_capture, attacker_size, defender_size 
        FROM battles
        Where battle_ID = ?
        ''', [id]).fetchone()
    
    if battle is None:
        abort(404, 'battle ID {} does not exist.'.format(id))

    region = db.execute(
        '''
        SELECT battle_name, region, region_id, battle_id
        FROM battles NATURAL JOIN regions
        WHERE battle_id = ?
        ''', [id]).fetchone()
    
    attack_commanders = db.execute(
        '''
        select character, character_id
        from characters join attack_commanders
        on character_id=attackcommander_id
        where battle_id=?
        ''', [id]).fetchall()
    
    defense_commanders = db.execute(
        '''
        select character, character_id
        from characters join defense_commanders
        on character_id=defense_commander_id
        where battle_id=?
        ''', [id]).fetchall()
    
    attacker_houses = db.execute(
        '''
        select house, house_id
        from attacks join houses
        on house_id=attackerhouse_id
        where battle_id=?
        ''', [id]).fetchall()
    
    defender_houses = db.execute(
        '''
        select house, house_id
        from defenses join houses
        on house_id=defenderhouse_id
        where battle_id=?
        ''', [id]).fetchall()
    
    attacker_king = db.execute(
        '''
        select character, character_id, imageUrl
        from battles join characters
        on character_id = attackerking_id
        where battle_id=?
        ''', [id]).fetchone()
    
    defender_king = db.execute(
        '''
        select character, character_id, imageUrl
        from battles join characters
        on character_id = defenderking_id
        where battle_id=?
        ''', [id]).fetchone()
    

    return render_template('battlesid.html', battle=battle, defender_king=defender_king, attacker_king=attacker_king, region=region, attack_commanders=attack_commanders, defense_commanders=defense_commanders, attacker_houses=attacker_houses, defender_houses=defender_houses)




############ CIDADES
@APP.route('/cities')
def cities():
    cities = db.execute(
        '''
        SELECT city, region, city_id
        FROM cities NATURAL JOIN regions
        ORDER BY city
        ''').fetchall()
    
    qtd = db.execute(
        '''
        SELECT count(city_id) AS qtd
        FROM cities;
        '''
        ).fetchone()
    
    return render_template('cities.html', cities=cities, qtd=qtd)

@APP.route('/cities/<int:id>/')
def get_city(id):
    city = db.execute(
        '''
        SELECT city_ID, city, region_id
        FROM cities
        Where city_ID = ?
        ''', [id]).fetchone()
    
    if city is None:
        abort(404, 'City ID {} does not exist.'.format(id))

    region = db.execute(
        '''
        SELECT city, region, region_id, city_id
        FROM cities NATURAL JOIN regions
        WHERE city_id = ?
        ''', [id]).fetchone()
    
    houses = db.execute(
        '''
        SELECT house_id, house
        FROM houses
        WHERE city_id = ?
        ''', [id]).fetchall()

    return render_template('citiesid.html', city=city, region=region, houses=houses)


############ PERSONAGENS
@APP.route('/characters')
def characters():
    characters = db.execute(
        '''
        SELECT character, character_ID, Title
        FROM characters
        ORDER BY character
        ''').fetchall()
    
    qtd = db.execute(
        '''
        SELECT count(character_id) AS qtd
        FROM characters;
        '''
        ).fetchone()
    return render_template('characters.html', characters=characters, qtd=qtd)
    
@APP.route('/characters/<int:id>/')
def get_character(id):
    character = db.execute(
        '''
        SELECT character_ID, character, title, gender, imageurl, is_king, house_id, house
        FROM characters natural join houses
        Where character_ID = ?
        ''', [id]).fetchone()
    
    if character is None:
        abort(404, 'character ID {} does not exist.'.format(id))

    king_battles = db.execute(
        '''
        select battle_name, battle_ID
        from battles
        where attackerking_ID=? or defenderking_ID=?
        ''', [id, id]).fetchall()
    
    command_battles = db.execute(
        '''
        select battle_id, battle_name
        from attack_commanders natural join battles
        where attackcommander_id=?

        union

        select battle_id, battle_name
        from defense_commanders natural join battles
        where defense_commander_id=?
        ''', [id, id]).fetchall()

    return render_template('charactersid.html', character=character, king_battles=king_battles, command_battles=command_battles)



if __name__ == '__main__':
    db.connect()
    APP.run(debug=True)