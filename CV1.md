- vložte alespoň 5 záznamů
```redis
MSET zaznam1 "hodnota1" zaznam2 "hodnota2" zaznam3 "hodnota3" zaznam4 "hodnota4" zaznam5 "hodnota5"
```

- zkontrolujte existenci klíče
```redis
EXISTS zaznam1
```

- vypište jeden ze záznamů
```redis
GET zaznam1
```

- jeden ze záznamů aktualizujte
```redis
SET zaznam1 "NOVA"
```

- jeden ze záznamů smažte
```redis
DEL zaznam2
```

- jeden ze záznamů nechte smazat za 60 sekund
```redis
EXPIRE zaznam3 60
TTL zaznam3
```

---
## TO-DO List

- seznam pojmenujte `todolist`, vložte do seznamu několik úkolů (úkoly vkládejte na konec seznamu)
```redis
RPUSH todolist "Ukol 1" "Ukol 2" "Ukol 3" "Ukol 4"
```

- vypište všechny úkoly
```
LRANGE todolist 0 -1
```

- vypište celkový počet úkolů
```
LLEN todolist
```

- dokončete vybraný úkol
```
LINDEX todolist 2
LREM todolist 0 "Ukol 3"
```

---
## Leaderboard

```
ZADD leaderboard 888 "Alfréd" 666 "Abrahám" 12 "Pavel" 9 "Lopata" 577 "Leoš" 599 "Amundsen" 797 "Matěj" 420 "Braunyj" 55 "Br" 99 "Posix" 410 "Fabián"
```

- Vypište 3 nejhorší hráče
```
ZREVRANGE leaderboard 0 2 WITHSCORES╔
```

- Zjistěte počet hráčů s méně než 100 body
```
    ZREVRANGEBYSCORE leaderboard 100 0 WITHSCORES
```

- Zjistěte počet hráčů s více než 850 body
```
ZREVRANGEBYSCORE leaderboard +inf 850 WITHSCORES
```

- Zjistěte Alfrédovu pozici v žebříčku
```
ZREVRANK leaderboard "Alfréd"
```

```
ZINCRBY leaderboard 12 "Alfréd"
```