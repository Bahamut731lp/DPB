Vytvoření indexu `person`

```http
PUT /person
```

Přidejte osobu s vaším jménem

```http
POST /person/_doc
{
  "name" : "Kevin Daněk"
}
```

Vypište vaší osobu
```http
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
```http
POST /person/_doc/OmdknocBoVt5oY6zBRIG
{
  "name" : "Devin Kaněk"
}
```

Vypište všechny dokumenty v indexu
```http
GET /person/_search
{
    "query": {
        "match_all": {}
    }
}
```

Smažte vybranou osobu
```http
DELETE /person/_doc/OmdknocBoVt5oY6zBRIG
```

Smažte index
```http
DELETE /person
```