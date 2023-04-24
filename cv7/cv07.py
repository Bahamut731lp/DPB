import urllib3
from elasticsearch import Elasticsearch

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
INDEX_NAME = 'person'

def print_delimiter(n):
    print('\n', '#' * 10, 'Úloha', n, '#' * 10, '\n')


# Připojení k ES
es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}], basic_auth=('elastic', '123456789'), verify_certs=False)

# Kontrola zda existuje index 'person'
if not es.indices.exists(index=INDEX_NAME):
    # Vytvoření indexu
    es.indices.create(index=INDEX_NAME)

# Index není potřeba vytvářet - pokud neexistuje, tak se automaticky vytvoří při vložení prvního dokumentu
doc = {
    "name": "Kevin Daněk"
}

# 1. Vložte osobu se jménem John
print_delimiter(1)
res = es.index(index=INDEX_NAME, id=1, document=doc)
print(res["result"])



# 2. Vypište vytvořenou osobu (pomocí get a parametru id)
print_delimiter(2)
res = es.get(index=INDEX_NAME, id=1)
print(res["_source"])



# 3. Vypište všechny osoby (pomocí search)
print_delimiter(3)
# Musíme refreshnout, jinak se tam ty výsledky neukážou
es.indices.refresh(index=INDEX_NAME)
res = es.search(index=INDEX_NAME, query={"match_all": {}})
print(res["hits"]['hits'])



# 4. Přejmenujte vytvořenou osobu na 'Jane'
print_delimiter(4)
res = es.index(index=INDEX_NAME, id=1, document={ "name": "Jane" })
print(res["result"])



# 5. Smažte vytvořenou osobu
print_delimiter(5)
res = es.delete(index=INDEX_NAME, id=1)
print(res["result"])



# 6. Smažte vytvořený index
print_delimiter(6)
res = es.indices.delete(index=INDEX_NAME)
print(res)
