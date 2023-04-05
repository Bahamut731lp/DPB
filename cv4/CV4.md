Vložení nové restaurace
```js
db.restaurants.insertOne(
    { 
        address: { 
            building: "420",
            coord: [0, 0],
            street: "Grove Street",
            zipcode: "11880"
        },
        borough: "Grove",
        cuisine: "Hoodish",
        grades: []
    }
)
```

Vypsání nově vložené restaurace
```js
db.restaurants.find().limit(1).sort(
    {
        $natural: -1
    }
)
```

Aktualizace nové restaurace
```js
db.restaurants.updateOne(
    {
        cuisine: "Hoodish"
    },
    {
        $set: {
            cuisine: "Ballas"
        }
    }
)
```

Přidání hodnocení restaurace
```js
db.restaurants.findAndModify(
    {
        query: {},
        sort: {
            $natural: -1
        },
        update: {
            $push: {
                grades: {
                    date: null,
                    grade: "A+",
                    score: 60
                }
            }
        }
    }
)
```

Smazání nové restaurace
```js
db.restaurants.findOneAndDelete(
    {
        cuisine: "Ballas"
    }
)
```

Vypsání všech restaurací
```js
db.restaurants.find()
```

Vypsání všech restaurací - pouze názvy
```js
db.restaurants.find(
    {},
    {
        name:1,
        _id:0
    }
)
```

Vypsání 10ti restaurací - pouze názvy
```js
db.restaurants.find(
    {},
    {
        name:1,
        _id:0
    }
).limit(10)
```

Vypsání dalších 10ti restaurací - pouze názvy
```js
db.restaurants.find(
    {}, 
    {
        name:1,
        _id:0
    }
).skip(10).limit(10)
```

Vypsání restarací ve čtvrti Bronx
```js
db.restaurants.find(
    {
        borough: "Bronx"
    }
)
```

Vypsání názvů restaurací, jejichž jméno začíná na M
```js
db.restaurants.find(
    {
        name: /^m/i
    }
)
```

Vypsání názvů restaurací, kteří vaří italskou kuchyni a sídlí na Manhattanu
```js
db.restaurants.find(
    {
        borough: "Manhattan",
        cuisine: "Italian"
    }
)
```

Vypsání názvů restaurací, kteří vaří italskou kuchyni a sídlí na Manhattanu
```js
db.restaurants.find(
    {
        "grades.score": {
            $gt: 80
        }
    }
)
```

Vypsání restaurací, které mají skóre mezi 80 a 90
```js
db.restaurants.find(
    {
        "grades": {
            $elemMatch: { 
                score: {
                    $gt: 80,
                    $lt: 90
                }
            }
        }
    }
)
```

Přidáno nového pole `popular: 1` k restauracím, které mají alespoň 1 skóre vyšší než 80.

```js
db.restaurants.updateMany(
    {
        "grades.score": { 
            $gt: 80
        }
    },
    {
        $set: {
            popular: 1
        }
    }
)
```

Přidáno nového pole `trash: 1` k restauracím, které mají alespoň 1 skóre nižší než 1.

```js
db.restaurants.updateMany(
    {
        "grades.score": { 
            $lt: 1
        }
    },
    {
        $set: {
            trash: 1
        }
    }
)
```

Vypsání kontroverzních restaurací
```js
db.restaurants.find(
    {
        trash: {
            $exists: true,
            $eq: 1
        },
        popular: {
            $exists: true,
            $eq: 1
        }
    }
)
```

Přidání nového pole `top_score: 1` ke všem hodnocením, které jsou vyšší než 90.
```js
db.restaurants.updateMany(
    {
        "grades.score": {
            $gt: 90
        }
    },
    {
        $set: {
            "grades.$[pr].top_score": 1
        }
    },
    { 
        arrayFilters: [ 
            {
                "pr.score": {
                    $gt: 90
                }
            }
        ]
    }
)
```