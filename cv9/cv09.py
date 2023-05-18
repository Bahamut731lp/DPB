import urllib3
import json
from elasticsearch import Elasticsearch
from tabulate import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_delimiter(n):
    print('\n', '#' * 10, 'Úloha', n, '#' * 10, '\n')


# Připojení k ES
es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}],
                   basic_auth=('elastic', '123456789'), verify_certs=False)


res = es.indices.delete(index="orders-new")

print_delimiter("Mapování")
mapping = {
    "properties": {
        "customer": {
            "type": "text"
        },
        "orders": {
            "properties": {
                "name": {"type": "text"},
                "id": {"type": "text"},
                "price": {"type": "float"},
                "quantity": {"type": "integer"}
            }
        }
    }
}
res = es.indices.create(index="orders-new", mappings=mapping)
# TODO: Zkásnout toma o řešení
print(res)

doc = {
    "customer": "Testovací zákazník",
    "orders": [
        {
            "name": "Instant Coffe",
            "product_id": "1",
            "price": 25,
            "quantity": 4
        },
        {
            "name": "Wine",
            "product_id": "85",
            "price": 249,
            "quantity": 1
        },
        {
            "name": "Cheese",
            "product_id": "44",
            "price": 85,
            "quantity": 50
        }
    ]
}

res = es.index(index="orders-new", id=1, document=doc)
print(res)


print_delimiter("Analyzéry")
analyzers = ["whitespace", "fingerprint", "keyword"]
for analyzer in analyzers:
    analysis_result = es.indices.analyze(
        analyzer=analyzer,
        text="Lorem ipsum dolor sit amet, consectetuer adipiscing elit."
    )

    print(analysis_result)


print_delimiter("Agregace")
# 1. Zjistěte minimální, maximální a průměrnou cenu produktů (bez použití stats)
print_delimiter(1)
aggregation = {
    "max_price": {
        "max": {
            "field": "price"
        }
    },
    "min_price": {
        "min": {
            "field": "price"
        }
    },
    "avg_price": {
        "avg": {
            "field": "price"
        }
    }
}
res = es.search(index="products", aggregations=aggregation)
print(tabulate([
    ["Minimum price", res["aggregations"]["min_price"]["value"]],
    ["Average price", res["aggregations"]["avg_price"]["value"]],
    ["Maximum price", res["aggregations"]["max_price"]["value"]]
], tablefmt="rounded_outline"))


# Zjistěte maximální, minimální a průměrnoý počet prodaných produktů (s použitím stats)
print_delimiter(2)
aggregation = {
    "sold_stats": {
        "stats": {
            "field": "sold"
        }
    }
}
res = es.search(index="products", aggregations=aggregation)
print(tabulate([
    ["Minimum sold", res["aggregations"]["sold_stats"]["min"]],
    ["Average sold", res["aggregations"]["sold_stats"]["avg"]],
    ["Maximum sold", res["aggregations"]["sold_stats"]["max"]]
], tablefmt="rounded_outline"))


# Pomocí dalšího dotaz zjistěte, který produkt se prodává nejvíce
print_delimiter("2a")
query = {
    "match": {
        "sold": res["aggregations"]["sold_stats"]["max"]
    }
}
max_sold_product = es.search(index="products", query=query)
print(json.dumps(max_sold_product["hits"]["hits"], indent=4))


# Pro každý tag zjistěte, v kolika dokumentech je obsažen
print_delimiter(3)

aggregation = {
    "total_tags": {
        "terms": {
            "field": "tags",
            "missing": "N/A",
            "order": {
                "_key": "asc"
            }
        }
    }
}

res = es.search(index="products", aggregations=aggregation)
print(res["aggregations"]["total_tags"])

# Zjistěte cenové statistiky pro jednotlivé tagy
print_delimiter(4)
aggregation = {
    "total_tags": {
        "terms": {
            "field": "tags",
            "missing": "N/A",
            "order": {
                "_key": "asc"
            }
        },
        "aggs": {
            "tag_prices": {
                "stats": {
                    "field": "price"
                }
            }
        }
    }
}

res = es.search(index="products", aggregations=aggregation)
print(res["aggregations"]["total_tags"])


print_delimiter("Bonus 1")
aggregation = {
    "total_tags": {
        "terms": {
            "field": "tags",
            "include": ["Cake", "Coffee"],
            "missing": "N/A",
            "order": {
                "_key": "asc"
            }
        },
        "aggs": {
            "tag_prices": {
                "stats": {
                    "field": "price"
                }
            }
        }
    }
}

res = es.search(index="products", aggregations=aggregation)
print(res["aggregations"]["total_tags"])


print_delimiter("Bonus 2")
aggregation = {
    "status_buckets": {
        "terms": {
            "field": "status",
            "missing": "N/A",
            "order": {
                "_key": "asc"
            }
        },
        "aggs": {
            "prices": {
                "stats": {
                    "field": "total_amount"
                }
            }
        }
    }
}

res = es.search(index="orders", aggregations=aggregation)
print(res["aggregations"]["status_buckets"])


print_delimiter("Bonus 3")
aggregation = {
    "quaterly_sales": {
        "date_range": {
            "field": "purchased_at",
            "missing": "0001-01-01",
            "ranges": [
                {
                    "key": "Q1",
                    "from": "2016-01-01",
                    "to": "2016-01-01||+3M"
                },
                {
                    "key": "Q2",
                    "from": "2016-01-01||+3M",
                    "to": "2016-01-01||+6M"
                }, {
                    "key": "Q3",
                    "from": "2016-01-01||+6M",
                    "to": "2016-01-01||+9M"
                }, {
                    "key": "Q4",
                    "from": "2016-01-01||+9M",
                    "to": "2016-01-01||+12M"
                },
                {
                    "key": "N/A",
                    "to": "0002-01-01"
                }
            ],
            "format": "yyyy-MM-dd"
        },
        "aggs": {
            "prices": {
                "stats": {
                    "field": "total_amount"
                }
            }
        }
    }
}

res = es.search(index="orders", aggregations=aggregation)
print(res["aggregations"]["quaterly_sales"])
