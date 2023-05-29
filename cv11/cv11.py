from datetime import datetime
from cassandra.cluster import Cluster
from tabulate import tabulate
import csv

'''
DPB - 11. cvičení Cassandra

Use case: Discord server - reálně používáno pro zprávy, zde pouze zjednodušená varianta.

Instalace python driveru: pip install cassandra-driver

V tomto cvičení se budou následující úlohy řešit s využitím DataStax driveru pro Cassandru.
Dokumentaci lze nalézt zde: https://docs.datastax.com/en/developer/python-driver/3.25/getting_started/


Optimální řešení (nepovinné) - pokud něco v db vytváříme, tak první kontrolujeme, zda to již neexistuje.

Pokud se Vám nedaří připojit se ke Cassandře v Dockeru, zkuste smazat kontejner a znovu spustit:

docker run --name dpb_cassandra -p 127.0.0.1:9042:9042 -p 127.0.0.1:9160:9160 -d cassandra:latest

'''


def print_delimiter(n):
    print('\n', '#' * 10, 'Úloha', n, '#' * 10, '\n')


def print_result(result):
    for row in result:
        print(row)


cluster = Cluster()  # automaticky se připojí k localhostu na port 9042
session = cluster.connect()

"""
1. Vytvořte keyspace 'dc' a přepněte se do něj (SimpleStrategy, replication_factor 1)
"""

print_delimiter(1)
res = session.execute(
"""
    CREATE KEYSPACE IF NOT EXISTS dc
    WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
"""
)

print(res)

session.set_keyspace("dc")

# """
# 2. V csv souboru message_db jsou poskytnuta data pro cvičení. V prvním řádku naleznete názvy sloupců.
#   Vytvořte tabulku messages - zvolte vhodné datové typy (time bude timestamp)
#   Primárním klíčem bude room_id a time
#   Data chceme mít seřazené podle času, abychom mohli rychle získat poslední zprávy
#
#   Jako id v této úloze zvolíme i time - zdůvodněte, proč by se v praxi time jako id neměl používat.
#
#   Pokud potřebujeme použít čas, tak se v praxi používá typ timeuuid nebo speciální identifikátor, tzv. Snowflake ID
#   (https://en.wikipedia.org/wiki/Snowflake_ID). Není potřeba řešit v tomto cvičení.
# """

print_delimiter(2)
res = session.execute(
"""
    CREATE TABLE IF NOT EXISTS messages (
        room_id int,
        speaker_id int,
        time timestamp,
        message text,
        PRIMARY KEY (room_id, time)
    ) 
    WITH CLUSTERING ORDER BY (time DESC);
"""
)

print(res)

#"""
#3. Do tabulky messages importujte message_db.csv
#   COPY není možné spustit pomocí DataStax driveru ( 'copy' is a cqlsh (shell) command rather than a CQL (protocol) command)
#   -> 2 možnosti:
#      a) Nakopírovat csv do kontejneru a spustit COPY příkaz v cqlsh konzoli uvnitř dockeru
#      b) Napsat import v Pythonu - otevření csv a INSERT dat
#CSV soubor může obsahovat chybné řádky - COPY příkaz automaticky přeskočí řádky, které se nepovedlo správně parsovat
#"""

print_delimiter(3)

insert_query = session.prepare(
    """
        INSERT INTO messages (room_id, speaker_id, time, message) \
        VALUES (?, ?, ?, ?)
    """
)

with open("message_db.csv", encoding="utf-8") as filehandle:
    message_reader = csv.reader(filehandle, delimiter=";")
    rows = session.execute("SELECT * from messages")
    next(message_reader)

    if len(rows.current_rows) == 0:
        for row in message_reader:
            session.execute(
                insert_query,
                (
                    int(row[0]),
                    int(row[1]),
                    datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'),
                    row[3]
                )
            )

"""
4. Kontrola importu - vypište 1 zprávu
"""

print_delimiter(4)
res = session.execute(
"""
    SELECT * 
    FROM messages
    LIMIT 1;
"""
)

print(res.current_rows)
"""
5. Vypište posledních 5 zpráv v místnosti 1 odeslaných uživatelem 2
    Nápověda 1: Sekundární index (viz přednáška) 
    Nápověda 2: Data jsou řazena již při vkládání
"""

print_delimiter(5)

# Vytvoření sekundárního indexu
session.execute(
    """
        CREATE INDEX IF NOT EXISTS users
        ON messages (speaker_id);
    """
)

res = session.execute(
    """
        SELECT * 
        FROM messages
        WHERE room_id = 1 AND speaker_id = 2;
    """
)

for row in res.current_rows:
    print(f'Uživatel {row.speaker_id} ({row.time}): {row.message}')

"""
6. Vypište počet zpráv odeslaných uživatelem 2 v místnosti 1
"""

print_delimiter(6)

res = session.execute(
    """
        SELECT COUNT(*) 
        FROM messages
        WHERE room_id = 1 AND speaker_id = 2;
    """
)

print(f'Místnosti 1: Uživatel 2 odeslal celkově {res.current_rows[0].count} zpráv.')

"""
7. Vypište počet zpráv v každé místnosti
"""

print_delimiter(7)
res = session.execute(
    """
        SELECT room_id, COUNT(*) 
        FROM messages
        GROUP BY room_id
    """
)
rows = [[f'Místnost {row.room_id}', row.count] for row in res.current_rows]
print(tabulate(rows, tablefmt="rounded_outline"))



"""
8. Vypište id všech místností (3 hodnoty)
"""

print_delimiter(8)
res = session.execute(
    """
        SELECT DISTINCT room_id
        FROM messages
    """
)
rows = [[row.room_id] for row in res]
print(tabulate(rows, tablefmt="rounded_outline"))



"""
Bonusové úlohy:

1. Pro textovou analýzu chcete poskytovat anonymizovaná textová data. Vytvořte Materialized View pro tabulku messages,
který bude obsahovat pouze čas, room_id a zprávu.

Vypište jeden výsledek z vytvořeného view

Před začátkem řešení je potřeba jít do souboru cassandra.yaml uvnitř docker kontejneru a nastavit enable_materialized_views=true

docker exec -it dpb_cassandra bash
sed -i -r 's/enable_materialized_views: false/enable_materialized_views: true/' /etc/cassandra/cassandra.yaml

Poté restartovat kontejner

2. Chceme vytvořit funkci (UDF), která při výběru dat vrátí navíc příznak, zda vybraný text obsahuje nevhodný výraz.

Vyberte jeden výraz (nemusí být nevhodný:), vytvořte a otestujte Vaši funkci.

Potřeba nastavit enable_user_defined_functions=true v cassandra.yaml

sed -i -r 's/enable_user_defined_functions: false/enable_user_defined_functions: true/' /etc/cassandra/cassandra.yaml

3. Zjistěte čas odeslání nejnovější a nejstarší zprávy.

4. Zjistěte délku nejkratší a nejdelší zprávy na serveru.	

5. Pro každého uživatele zjistěte průměrnou délku zprávy.		

V celém cvičení by nemělo být použito ALLOW FILTERING.
"""
