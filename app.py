import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import Flask, render_template, abort
import logging
import db

APP = Flask(__name__)

# Start Page
@APP.route('/')
def index():
    return render_template('index.html')

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

@APP.route('/houses/search/<expr>/')
def search_house(expr):
  if (not str.isalpha(expr)):
      abort(404, 'expression is not valid')
      
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  houses = db.execute(
      ''' 
      SELECT House, House_ID, Words
      FROM Houses
      WHERE House LIKE ?
      ''', [expr]).fetchall()
  
  if not houses:
      abort(404, 'there are no houses with this expression')

  return render_template('housesearch.html', search=search, houses=houses)

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


@APP.route('/battles/search/<expr>/')
def search_battle(expr):
  if (not str.isalpha(expr)):
      abort(404, 'expression is not valid')
      
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  battles = db.execute(
      ''' 
      SELECT battle_name, battle_ID, battle_type, year
      FROM battles
      WHERE battle_name LIKE ?
      ''', [expr]).fetchall()
  
  if not battles:
      abort(404, 'there are no battles with this expression')
      
  return render_template('battlesearch.html', search=search, battles=battles)


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

@APP.route('/cities/search/<expr>/')
def search_city(expr):
  if (not str.isalpha(expr)):
      abort(404, 'expression is not valid')
      
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  cities = db.execute(
      ''' 
      SELECT city, region, city_id
      FROM cities NATURAL JOIN regions
      WHERE city LIKE ?
      ''', [expr]).fetchall()
  
  if not cities:
      abort(404, 'there are no cities with this expression')
      
  return render_template('citysearch.html', search=search, cities=cities)


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


@APP.route('/characters/search/<expr>/')
def search_character(expr):
  if (not str.isalpha(expr)):
      abort(404, 'expression is not valid')
      
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  characters = db.execute(
      ''' 
      SELECT character, character_ID, Title
      FROM characters
      WHERE character LIKE ?
      ''', [expr]).fetchall()
  
  if not characters:
      abort(404, 'there are no characters with this expression')
      
  return render_template('charactersearch.html', search=search, characters=characters)

@APP.route('/curiosities')
def curiosities():
    mostAttackedHouses = db.execute(
        '''
        SELECT h.House AS Defender_House, COUNT(d.Battle_ID) AS Total_Attacks, h.house_id
        FROM Houses h
        JOIN Defenses d ON h.House_ID = d.DefenderHouse_ID
        GROUP BY h.House
        ORDER BY Total_Attacks DESC
        LIMIT 3;
        '''
    ).fetchall()

    highestDeathsByBattle = db.execute(
        '''
        SELECT Battle_Name AS Batalha, (Attacker_size + Defender_size) AS Total_de_Mortes, battle_id
        FROM Battles
        WHERE Attacker_size IS NOT NULL AND Defender_size IS NOT NULL
        ORDER BY Total_de_Mortes DESC
        LIMIT 3;
        '''
    ).fetchall()

    highestBattlesByRegion = db.execute(
        '''
        SELECT r.Region AS Region_Name, COUNT(b.Battle_ID) AS Total_Battles, r.region_id as rID
        FROM Regions r
        JOIN Battles b ON r.Region_ID = b.Region_ID
        GROUP BY r.Region
        ORDER BY Total_Battles DESC
        LIMIT 3;
        '''
    ).fetchall()

    mostEvenBattles = db.execute(
        '''
        SELECT Battle_Name, ABS(Attacker_size - Defender_size) AS Size_Difference, battle_id
        FROM Battles
        WHERE Attacker_size IS NOT NULL AND Defender_size IS NOT NULL
        ORDER BY Size_Difference ASC
        LIMIT 3;
        '''
    ).fetchall()

    mostHousesByRegion = db.execute(
        '''
        SELECT r.Region AS Region_Name, COUNT(h.House_ID) AS Total_Houses, r.region_id as rID
        FROM Regions r
        JOIN Cities c ON r.Region_ID = c.Region_ID
        JOIN Houses h ON c.City_ID = h.City_ID
        GROUP BY r.Region
        ORDER BY Total_Houses DESC
        LIMIT 3;
        '''
    ).fetchall()

    avgHousesByRegion = db.execute(
        '''
        SELECT AVG(house_count) AS avg, MAX(house_count) AS max, MIN(house_count) AS min
        FROM (
            SELECT Region_ID, COUNT(*) AS house_count
            FROM Cities c
            JOIN Houses h ON c.City_ID = h.City_ID
            GROUP BY Region_ID
            )   
        '''
    ).fetchone()

    charactersByGender = db.execute(
        '''
        SELECT Gender, (COUNT() * 100.0 / (SELECT COUNT() FROM Characters)) AS percentage
        FROM Characters
        GROUP BY Gender;
        '''
    ).fetchall()
    
    return render_template('curiosities.html', mostAttackedHouses=mostAttackedHouses, highestDeathsByBattle=highestDeathsByBattle, highestBattlesByRegion=highestBattlesByRegion, mostEvenBattles=mostEvenBattles, mostHousesByRegion=mostHousesByRegion, avgHousesByRegion=avgHousesByRegion, charactersByGender=charactersByGender)

if __name__ == '__main__':
    db.connect()
    APP.run(debug=True)