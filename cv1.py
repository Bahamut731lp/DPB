import redis

r = redis.Redis(host="127.0.0.1", port=6379, db=0)

r.delete("leaderboard")

r.zadd("leaderboard", {"Alfréd": 888})
r.zadd("leaderboard", {"Abrahám": 666})
r.zadd("leaderboard", {"Pavel": 12})
r.zadd("leaderboard", {"Lopata": 9})
r.zadd("leaderboard", {"Leoš": 577})
r.zadd("leaderboard", {"Matěj": 599})
r.zadd("leaderboard", {"Braunyj": 345})
r.zadd("leaderboard", {"Br": 12})
r.zadd("leaderboard", {"Posix": 122})
r.zadd("leaderboard", {"Fabián": 420})

print(f'Tři nejlepší: {r.zrevrange("leaderboard", 0, 2)}')
worstScore = r.zrangebyscore("leaderboard", "-inf", "+inf", withscores=True, start=0, num=1)
print(f'Nejhorší skóre: {worstScore}')
print(f'<100: {r.zrevrangebyscore("leaderboard", 100, 0, withscores=True)}')
print(f'>850: {r.zrevrangebyscore("leaderboard", "+inf", 850, withscores=True)}')
print(f'Alfréd: {r.zrevrank("leaderboard", "Alfréd")}')
r.zincrby("leaderboard", 12, "Alfréd")
print(f'>850: {r.zrevrangebyscore("leaderboard", "+inf", 850, withscores=True)}')