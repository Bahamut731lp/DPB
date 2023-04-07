"""
    Cvičení 5 z DPB - Mongo pt.2 : Electric Boogaloo

    Implementujte jednotlivé body pomocí PyMongo knihovny.
    Rozhraní je téměř stejné jako v Mongo shellu.
    Před testováním Vašich řešení si nezapomeňte zapnout Mongo v Dockeru.

    Pro pomoc je možné např. použít https://www.w3schools.com/python/python_mongodb_getstarted.asp

    Funkce find vrací kurzor - pro vypsání výsledku je potřeba pomocí foru iterovat nad kurzorem:
    cursor = collection.find(...)
    for restaurant in cursor:
        print(restaurant) # případně print(restaurant['name'])

    Všechny výsledky limitujte na 10 záznamů. Nepoužívejte české názvy proměnných!
"""
import re
import sys
from datetime import datetime
from pymongo import MongoClient, ASCENDING

sys.stdout = open('./output.log', 'w', encoding="utf-8")

client = MongoClient()
db = client.get_database("cv04")

def print_delimiter(exercise_index: int):
    """
    Funkce pro vytisknutí oddělovače úhlohy
    """
    print('\n', '#' * 10, 'Úloha', exercise_index, '#' * 10, '\n')



# 1. Vypsání všech restaurací
print_delimiter(1)
all_restaurants = db.restaurants.find().limit(10)
for restaurant in all_restaurants:
    print(restaurant)



# 2. Vypsání všech restaurací - pouze názvů, abecedně seřazených
print_delimiter(2)
all_restaurants_names = (
    db
    .restaurants
    .find(
        {},
        {
            "name": 1,
            "_id": 0
        }
    )
    .sort("name", ASCENDING)
)
for restaurant in all_restaurants_names.clone().limit(10):
    print(restaurant["name"])



# 3. Vypsání pouze 5 záznamů z předchozího dotazu
print_delimiter(3)
for restaurant in all_restaurants_names.clone().limit(5):
    print(restaurant["name"])



# 4. Zobrazte dalších 10 záznamů
print_delimiter(4)
for restaurant in all_restaurants_names.skip(10).limit(10).sort("name", ASCENDING):
    print(restaurant["name"])



# 5. #Vypsání restaurací ve čtvrti Bronx (čtvrť = borough)
print_delimiter(5)
bronx_restaurants = (
    db
    .restaurants
    .find(
        {
            "borough": "Bronx"
        },
        {
            "name": 1,
            "borough": 1
        }
    )
    .limit(10)
)
for restaurant in bronx_restaurants:
    print(restaurant)



# 6. Vypsání restaurací, jejichž název začíná na písmeno M
print_delimiter(6)
regx = re.compile("^m", re.IGNORECASE)
restaurants_with_m = (
    db
    .restaurants
    .find({"name": regx})
    .limit(10)
)
for restaurant in restaurants_with_m:
    print(restaurant["name"])



# 7. Vypsání restaurací, které mají skóre větší než 80
print_delimiter(7)
greater_than_80 = (
    db
    .restaurants
    .find(
        {
            "grades.score": {
                "$gt": 80
            }
        },
        {
            "name": 1,
            "_id": 0
        }
    )
)
for restaurant in greater_than_80:
    print(restaurant)



# 8. Vypsání restaurací, které mají skóre mezi 80 a 90
print_delimiter(8)
restaurants_in_range = (
    db
    .restaurants
    .find(
        {
            "$and": [
                {
                    "grades.score": {
                        "$gt": 80
                    }
                },
                {
                    "grades.score": {
                        "$lt": 90
                    }
                }
            ]
        },
        {
            "name": 1,
            "_id": 0,
            "grades": 1
        }
    )
)
for restaurant in restaurants_in_range:
    print(restaurant["name"])



# Bonusové úlohy:

# 9. Vypsání všech restaurací, které mají skóre mezi 80 a 90
# a zároveň nevaří americkou kuchyni
# V datech je "American " (důraz na mezeru na konci) - proto regex
print_delimiter(9)
american_regx = re.compile("american", re.IGNORECASE)
restaurants_in_range_without_american = (
    db
    .restaurants
    .find(
        {
            "$and": [
                {
                    "cuisine": {
                        "$not": american_regx
                    }
                },
                {
                    "grades.score": {
                        "$gt": 80
                    }
                },
                {
                    "grades.score": {
                        "$lt": 90
                    }
                }
            ]
        })
    .limit(10)
)
for restaurant in restaurants_in_range_without_american:
    print(f'{restaurant["name"]} - {restaurant["cuisine"]}')



# 10. Vypsání všech restaurací, které mají alespoň osm hodnocení
print_delimiter(10)
more_than_eight_reviews = (
    db
    .restaurants
    .find(
        {
            "grades.7": {
                "$exists": True
            }
        }
    )
    .limit(10)
)
for restaurant in more_than_eight_reviews:
    print(f'{restaurant["name"]} - {len(restaurant["grades"])}')



# 11. Vypsání všech restaurací, které mají alespoň jedno hodnocení z roku 2014
print_delimiter(11)
old_reviews = (
    db
    .restaurants
    .find(
        {
            "grades.date": {
                "$gte": datetime(2014, 1, 1),
                "$lt": datetime(2015, 1, 1)
            }
        }
    )
    .limit(10)
)
for restaurant in old_reviews:
    years = list(map(lambda r: r["date"].year, restaurant["grades"]))
    print(f'{restaurant["name"]} - {years}')

#V této části budete opět vytvářet vlastní restauraci.
#
#Řešení:
#Vytvořte si vaši restauraci pomocí slovníku a poté ji vložte do DB.
#restaurant = {...}

# 12. Uložte novou restauraci (stačí vyplnit název a adresu)
print_delimiter(12)

my_restaurant = {
    "address": {
        "building": "420",
        "coord": [0, 0],
        "street": "Okružní",
        "zipcode": "47069"
    },
    "name": "U Suchý dásně",
    "borough": "Sever",
    "cuisine": "Co hood dal",
    "grades": []
}

insert_result = (
    db
    .restaurants
    .insert_one(my_restaurant)
)
print(insert_result.acknowledged, insert_result.inserted_id)



# 13. Vypište svoji restauraci
print_delimiter(13)
my_restaurant_from_db = (
    db
    .restaurants
    .find(
        {
            "name": "U Suchý dásně"
        }
    )
    .limit(10)
)
for restaurant in my_restaurant_from_db:
    print(f'{restaurant["name"]}')



# 14. Aktualizujte svoji restauraci - změňte libovolně název
print_delimiter(14)
updated_restaurant = (
    db
    .restaurants
    .find_one_and_update(
        {
            "name": "U Suchý dásně"
        },
        {
            "$set": {
                "name": "Mokrá ústřice"
            }
        }
    )
)
print(dict(updated_restaurant))


# 15. Smažte svoji restauraci
# 15.1 pomocí id (delete_one)
# 15.2 pomocí prvního nebo druhého názvu (delete_many, využití or)
print_delimiter(15)
deletion_result = (
    db
    .restaurants
    .delete_one(
        {
            "_id": updated_restaurant["_id"]
        }
    )
)

bulk_deletion_result = (
    db
    .restaurants
    .delete_many(
        {
            "$or": [
                {
                    "name": "Mokrá ústřice"
                },
                {
                    "name": "U Suchý dásně"
                }
            ]
        }
    )
)

print(deletion_result.acknowledged, deletion_result.deleted_count)
print(bulk_deletion_result.acknowledged, bulk_deletion_result.deleted_count)

# Poslední částí tohoto cvičení je vytvoření jednoduchého indexu.
# Použijte např. 3. úlohu s vyhledáváním čtvrtě Bronx.
# První použijte Váš již vytvořený dotaz a na výsledek použijte: cursor.explain()['executionStats']
# výsledek si vypište na výstup a všimněte si položky 'totalDocsExamined'
# Poté vytvořte index na 'borough', zopakujte dotaz a porovnejte hodnoty 'totalDocsExamined'.
# S řešením pomůže
# https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.create_index

print_delimiter(16)
non_indexed_docs_count = (
    bronx_restaurants
    .explain()
    ["executionStats"]
    ["totalDocsExamined"]
)

index = (
    db
    .restaurants
    .create_index("borough")
)

indexed_borough_query = (
    db
    .restaurants
    .find(
        {
            "borough": "Bronx"
        },
        {
            "name": 1, "borough": 1
        }
    )
    .limit(10)
)
indexed_docs_count = (
    indexed_borough_query
    .explain()
    ["executionStats"]
    ["totalDocsExamined"]
)

print(non_indexed_docs_count)  # 155
print(indexed_borough_query)  # 10

db.restaurants.drop_index(index)
