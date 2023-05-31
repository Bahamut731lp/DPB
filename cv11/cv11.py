from datetime import datetime
import math
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

# """
# 3. Do tabulky messages importujte message_db.csv
#   COPY není možné spustit pomocí DataStax driveru ( 'copy' is a cqlsh (shell) command rather than a CQL (protocol) command)
#   -> 2 možnosti:
#      a) Nakopírovat csv do kontejneru a spustit COPY příkaz v cqlsh konzoli uvnitř dockeru
#      b) Napsat import v Pythonu - otevření csv a INSERT dat
# CSV soubor může obsahovat chybné řádky - COPY příkaz automaticky přeskočí řádky, které se nepovedlo správně parsovat
# """

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

print(
    f'Místnosti 1: Uživatel 2 odeslal celkově {res.current_rows[0].count} zpráv.')

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


# """
# Bonusové úlohy:

# 1. Pro textovou analýzu chcete poskytovat anonymizovaná textová data. Vytvořte Materialized View pro tabulku messages, který bude obsahovat pouze čas, room_id a zprávu.
# Vypište jeden výsledek z vytvořeného view

print_delimiter("Bonusová 1")

res = session.execute(
    """
        CREATE MATERIALIZED VIEW IF NOT EXISTS anon_messages AS
            SELECT time, room_id, message
            FROM messages
            WHERE room_id IS NOT NULL AND message IS NOT NULL AND time IS NOT NULL
            PRIMARY KEY (room_id, time)
            WITH CLUSTERING ORDER BY (time DESC);
    """
)

res = session.execute(
    """
    SELECT * 
    FROM anon_messages
    LIMIT 1;
"""
)

print(res.current_rows)


# 2. Chceme vytvořit funkci (UDF), která při výběru dat vrátí navíc příznak, zda vybraný text obsahuje nevhodný výraz.
print_delimiter("Bonusová 2")
session.execute(
    """
        CREATE OR REPLACE FUNCTION check_inappropriate(text_value text)
        CALLED ON NULL INPUT
        RETURNS boolean
        LANGUAGE java
        AS '
            return text_value.contains("I");
        ';
    """
)

res = session.execute(
    """
        SELECT message, check_inappropriate(message) AS is_inappropriate
        FROM messages
        LIMIT 10;
    """
)
rows = [[row.message, row.is_inappropriate] for row in res]
print(tabulate(rows, tablefmt="rounded_outline"))


# 3. Zjistěte čas odeslání nejnovější a nejstarší zprávy.
res = session.execute(
    """
        SELECT MAX(time) AS newest_message, MIN(time) AS oldest_message
        FROM messages;
    """
)
rows = []
for row in res:
    rows.extend([
        ["Newest Message", row.newest_message],
        ["Oldest Message", row.oldest_message]
    ]
)

# 4. Zjistěte délku nejkratší a nejdelší zprávy na serveru.
print_delimiter("Bonusová 4")
session.execute(
    """
        CREATE FUNCTION IF NOT EXISTS LENGTH (input text) 
        CALLED ON NULL INPUT 
        RETURNS int 
        LANGUAGE java AS '
            return input.length();
        ';
    """
)
res = session.execute(
    """
        SELECT MIN(LENGTH(message)) AS shortest_message_length, 
        MAX(LENGTH(message)) AS longest_message_length
        FROM messages;
    """
)

for row in res:
    rows.extend([
        ["Shortest Message Length", row.shortest_message_length], 
        ["Longest Message Length", row.longest_message_length]
    ]
)
print(tabulate(rows, tablefmt="rounded_outline"))



# 5. Pro každého uživatele zjistěte průměrnou délku zprávy.
print_delimiter("Bonusová 5")

# Tady to prcám.
# Cassandra na tohle nemá nástroje, které by se daly použít bez toho, aniž by ses zbláznil
# V Pythonu to bude mnohem rychlejší.
res = session.execute(
    """
        SELECT speaker_id, LENGTH(message) as message_length
        FROM messages
    """
)

users = {}
for speaker_id, message_length in res:
    if speaker_id not in users:
        users[speaker_id] = { "count": 0, "size": 0 }

    users[speaker_id]["count"] += 1
    users[speaker_id]["size"] += message_length

rows = [[key, math.floor(value["size"] / value["count"])] for key, value in users.items()]
rows = sorted(rows, key=lambda x: x[0])
print(
    tabulate(
        rows,
        tablefmt="rounded_outline",
        headers=["Uživatel", "Průměrný počet znaků na zprávu"]
    )
)

# V celém cvičení by nemělo být použito ALLOW FILTERING.
