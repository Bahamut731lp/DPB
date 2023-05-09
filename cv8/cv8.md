# Vyhledávání produktů

1. Vytvořte dotaz pro vyhledávání výrazu (term) `coffee` v názvu produktu

```json
GET /products/_search
{
  "query": {
    "term": {
      "name": "coffee"
    }
  }
}
```

- Kolik výsledků vrátí?

```json
{
  "took": 15,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 11,
      "relation": "eq"
    },
    "max_score": 5.1803083,
    "hits": [...]
  }
}
```

---

2. Upravte dotaz tak, any fungoval i v případě jednoho uživatelského překlepu
   (např. stejné výsledky pro `cofee` nebo `coffe`)

```json
GET /products/_search
{
  "query": {
    "match": {
      "name": {
        "query": "coffee",
        "fuzziness": "1"
      }
    }
  }
}
```

```json
{
  "took": 4,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 12,
      "relation": "eq"
    },
    "max_score": 5.1803083,
    "hits": [...]
  }
}
```

- Co se stane po povolení více než jednoho překlepu?

> Čas na vykonání je větší, ale počet výsledků se neliší.

---

3. Vytvořte dotaz, který vyhledá produkty s tagem `Coffee` (term)

```json
GET /products/_search
{
  "query": {
    "terms": {
      "tags.keyword": [
        "Coffee"
      ]
    }
  }
}
```

```json
{
  "took": 3,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 12,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [...]
    }
}
```

- Liší se počet výsledků? Pokud ano, který název nenalezl první dotaz a proč?

> Oproti prvnímu dotazu se výsledek liší o jeden nález, a protože ho nalezl
> upravený dotaz povolující překlepy, bude to právě kvůli překlepu.

---

4. Najděte produkty s tagem `Coffee` s 10 nebo méně kusy na skladě (`in_stock`)

```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "terms": {
            "tags": [
              "Coffee"
            ]
          }
        },
        {
          "range": {
            "in_stock": {
              "lte": 10
            }
          }
        }
      ]
    }
  }
}
```

```json
{
  "took": 3,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 2,
    "hits": [
      {
        "_index": "products",
        "_id": "kvJ4AogB-aI6AkTYRvMM",
        "_score": 2,
        "_source": {
          "name": "Coffee Cup 8oz 5338cd",
          "price": 37,
          "in_stock": 0,
          "sold": 231,
          "tags": [
            "Coffee"
          ],
          "description": "Morbi ut odio. Cras mi pede, malesuada in, imperdiet et, commodo vulputate, justo. In blandit ultrices enim. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Proin interdum mauris non ligula pellentesque ultrices. Phasellus id sapien in sapien iaculis congue.",
          "is_active": false,
          "created": "2002/10/15"
        }
      }
    ]
  }
}
```

5. Najděte produkty, které v názvu mají `coffee`, ale neobsahují `cup`.

```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "name": "coffee"
          }
        }
      ],
      "must_not": [
        {
          "term": {
            "name": "cup"
          }
        }
      ]
    }
  }
}
```

```json
{
    "took":4,
    "timed_out":false,
    "_shards":{
        "total":1,
        "successful":1,
        "skipped":0,
        "failed":0
    },
    "hits":{
        "total":{
            "value":6,
            "relation":"eq"
        },
        "max_score":5.1803083,
        "hits":[
            "..."
        ]
    }
}
```
---
6. Vyfiltrujte všechny produkty, které byly přidány po roce 2000

```json
GET /products/_search
{
  "query": {
    "bool": {
      "filter": [
        {
          "range": {
            "created": {
              "gte": "2000-01-01"
            }
          }
        }
      ]
    }
  }
}
```

```json
{
   "took":14,
   "timed_out":false,
   "_shards":{
      "total":1,
      "successful":1,
      "skipped":0,
      "failed":0
   },
   "hits":{
      "total":{
         "value":1000,
         "relation":"eq"
      },
      "max_score":0,
      "hits":[
         "..."
      ]
   }
}
```

---
7. Full-textově vyhledejte produkty obsahující v názvu `Red Wine`

```json
GET /products/_search
{
  "query": {
    "match_phrase": {
      "name": "Red Wine"
    }
  }
}
```

```json
{
   "took":12,
   "timed_out":false,
   "_shards":{
      "total":1,
      "successful":1,
      "skipped":0,
      "failed":0
   },
   "hits":{
      "total":{
         "value":1,
         "relation":"eq"
      },
      "max_score":6.4624066,
      "hits":[
         {
            "_index":"products",
            "_id":"dvJ4AogB-aI6AkTYRvEH",
            "_score":6.4624066,
            "_source":{
               "name":"Vinegar - Red Wine",
               "price":124,
               "in_stock":13,
               "sold":4,
               "tags":[
                  "Alcohol",
                  "Wine"
               ],
               "description":"Morbi sem mauris, laoreet ut, rhoncus aliquet, pulvinar sed, nisl. Nunc rhoncus dui vel sem. Sed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci. Nullam molestie nibh in lectus. Pellentesque at nulla.",
               "is_active":true,
               "created":"2006/06/06"
            }
         }
      ]
   }
}
```

---
8. Vytvořte dotaz, který bude fungovat jako našeptávač při vyhledávání
- Začne vracet nejvíce relevantní výsledky během psaní
- např. uživatel napíše pouze znak `c` a už jsou mu vraceny první výsledky
- zadaný řetězec se může nacházet kdekoliv v názvu
- doporučujte pouze 5 relevantních výsledků
- vyzkoušejte si postupně vyhledávat `c`, `co`, ..., `coffee`

```json
GET /products/_search
{
  "size": 5,
  "query": {
    "wildcard": {
      "name": {
        "value": "*coffee*"
      }
    }
  }
}
```

|pattern|result|
|:--:|:--:|
|`*c*`|522|
|`*co*`|132|
|`*cof*`|12|
|`*coff*`|12|
|`*coffe*`|12|
|`*coffee*`|12|

---
9. Vytvořte dotaz, který bude vracet recepty, v nichž se nachází libovolný výraz.
- Hledaný výraz může být v nadpisu, popisu nebo ingrediencích receptu
- např. spaghetti

```json
GET /recipes/_search
{
  "query": {
    "query_string": {
      "query": "spaghetti",
      "fields": ["title", "description", "ingredients.name"]
    }
  }
}
```


---
10. Vytvořte dotaz, který bude v názvu hledat frázi "Pasta Carbonara"

```json
GET /recipes/_search
{
  "query": {
    "query_string": {
      "query": "spaghetti",
      "fields": ["title", "description", "ingredients.name"]
    }
  }
}
```

- Dotaz rozšiřte o hledání v blízkosti, aby výsledkem byl i výraz "Carbonara Pasta"

```json
GET /recipes/_search
{
  "query": {
    "query_string": {
      "query": "\"Pasta Carbonara\"",
      "default_field": "title"
    }
  }
}
```

- Kolik je výsledků?
> 0

```json
GET /recipes/_search
{
  "query": {
    "query_string": {
      "query": "\"Pasta Carbonara\"~2",
      "default_field": "title"
    }
  }
}
```
> 1