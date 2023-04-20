'''
DPB - 6. cvičení - Agregační roura a Map-Reduce

V tomto cvičení si můžete vybrat, zda ho budete řešit v Mongo shellu nebo pomocí PyMongo knihovny.
Před testováním Vašich řešení si nezapomeňte zapnout Mongo v Dockeru - používáme stejná data jako v minulých cvičeních.
Pro pomoc je možné např. použít https://api.mongodb.com/python/current/examples/aggregation.html a přednášku.
Všechny výsledky limitujte na 10 záznamů. Nepoužívejte české názvy proměnných!
Struktura záznamu v db:
{
  "address": {
     "building": "1007",
     "coord": [ -73.856077, 40.848447 ],
     "street": "Morris Park Ave",
     "zipcode": "10462"
  },
  "borough": "Bronx",
  "cuisine": "Bakery",
  "grades": [
     { "date": { "$date": 1393804800000 }, "grade": "A", "score": 2 },
     { "date": { "$date": 1378857600000 }, "grade": "A", "score": 6 },
     { "date": { "$date": 1358985600000 }, "grade": "A", "score": 10 },
     { "date": { "$date": 1322006400000 }, "grade": "A", "score": 9 },
     { "date": { "$date": 1299715200000 }, "grade": "B", "score": 14 }
  ],
  "name": "Morris Park Bake Shop",
  "restaurant_id": "30075445"
}
'''
import re
import sys
from datetime import datetime
from pymongo import MongoClient, ASCENDING

#sys.stdout = open('./output.log', 'w', encoding="utf-8")

client = MongoClient()
db = client.get_database("cv04")

def print_delimiter(exercise_index: int):
    """
    Funkce pro vytisknutí oddělovače úhlohy
    """
    print('\n', '#' * 10, 'Úloha', exercise_index, '#' * 10, '\n')

# Agregační roura
# Zjistěte počet restaurací pro každé PSČ (zipcode)
#  a) seřaďte podle zipcode vzestupně
#  b) seřaďte podle počtu restaurací sestupně
# Výpis limitujte na 10 záznamů a k provedení použijte collection.aggregate(...)
print_delimiter("1a")
grouped_by_zip__ascending_zip = (
    db
    .restaurants
    .aggregate([
        { "$group" : { "_id" : "$address.zipcode", "count": {"$count": {}} } },
        { "$sort": { "_id" : 1 } },
        { "$limit": 10 }
    ])
)
for restaurant in grouped_by_zip__ascending_zip:
    print(restaurant)



print_delimiter("1b")
grouped_by_psc__descending_count = (
    db
    .restaurants
    .aggregate([
        { "$group" : { "_id" : "$address.zipcode", "count": {"$count": {}} } },
        { "$sort": { "count" : -1 } },
        { "$limit": 10 }
    ])
)
for restaurant in grouped_by_psc__descending_count:
    print(restaurant)



print_delimiter(2)
grades_values = (
    db
    .restaurants
    .aggregate([
        { "$unwind": "$grades" },
        { "$group": { "_id": "$grades.grade", "average": { "$avg": "$grades.score" } } },
        { "$match": { "_id": { "$ne": "Not Yet Graded" } } },
        { "$limit": 10 }
    ])
)
for grading in grades_values:
    print(grading)



print_delimiter(3)
# Zcela upřímně nechápu, co se po mě Luky chce.
top_5_restaurants = (
    db
    .restaurants
    .aggregate([
        { "$addFields": { "grades_count": { "$size": "$grades" }}},
        { "$match": { "grades_count": { "$gt": 3 }}},
        { "$unwind": "$grades" },
        { "$group": { "_id": {"name": "$name", "grade": "$grades.grade"}, "score": {"$avg": "$grades.score"}}},
        { "$sort": { "score": -1 }},
        { "$match": { "_id.grade": { "$eq": "A" }}},
        { "$limit": 5 }
    ])
)
for grading in top_5_restaurants:
    print(grading)



print_delimiter(4)
top_5_cuisine = (
    db
    .restaurants
    .aggregate([
        { "$addFields": { "grades_count": { "$size": "$grades" }}},
        { "$match": { "grades_count": { "$gt": 3 }}},
        { "$unwind": "$grades" },
        { "$group": { "_id": {"name": "$name", "grade": "$grades.grade"}, "grades_count": {"$first": "$grades_count"}, "cuisine": {"$first": "$cuisine"}, "score": {"$avg": "$grades.score"}}},
        { "$sort": { "score": -1 }},
        { "$group": { "_id": "$cuisine", "restaurant": { "$first":  "$_id.name"}, "grades_count": {"$first": "$grades_count"}}}
    ])
)
for grading in top_5_cuisine:
    print(grading)



print_delimiter(5)
mutliword_name = (
    db
    .restaurants
    .aggregate([
        { "$unwind": "$grades" },
        { "$group": { "_id": "$name", "reviews": { "$push": "$grades.score" }} },
        { "$project": { "_id": 1, "reviews": { "$maxN": { "input": "$reviews", "n": 2 } }} },
        { "$project": { "_id": 1, "reviews": { "$map": { "input": "$reviews", "as": "score", "in": { "$gt": ["$$score", 10]}}}}},
        { "$project": { "_id": 1, "reviews": { "$allElementsTrue": ["$reviews"]}}},
        { "$match": { "reviews": True }},
        { "$addFields": { "length": { "$size": { "$split": ["$_id", " "] }}}},
        { "$match": { "length": { "$gt": 1 }}},
        { "$project": { "_id": 1 }},
        { "$limit": 10 }
    ])
)
for grading in mutliword_name:
    print(grading)
