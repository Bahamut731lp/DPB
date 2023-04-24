Vytvoření indexu `person`

```http
PUT /person
```

Přidejte osobu s vaším jménem

```
POST /person/_doc
{
  "name" : "Kevin Daněk"
}
```

Vypište vaší osobu
```
GET /person/_doc/OmdknocBoVt5oY6zBRIG
GET /person/_search
{
    "query": {
        "match": {
            "name": "Kevin Daněk"
        }
    }
}
```

Přejmenujte vaši osobu
```
POST /person/_doc/OmdknocBoVt5oY6zBRIG
{
  "name" : "Devin Kaněk"
}
```

Vypište všechny dokumenty v indexu
```
GET /person/_search
{
    "query": {
        "match_all": {}
    }
}
```

Smažte vybranou osobu
```
DELETE /person/_doc/OmdknocBoVt5oY6zBRIG
```

Smažte index
```
DELETE /person
```