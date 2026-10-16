from Config.redisConnection import redisConnect

def AddRateLimmiter(userid:str, limit:int=100,ttl:int=60):
    try:
        setlimit = redisConnect.hset(userid,'limit',limit)
        setttl = redisConnect.expire(userid,ttl)
        return "limit has been set"
    except Exception as e:
        print(e)
        return "Error occured while setting limit"

async def UpdateRateLimmiter(userid:str):
    getlimit = redisConnect.hget(userid,'limit')
    getttl = redisConnect.ttl(userid)

    if (getttl==-2):
        AddRateLimmiter(userid)
        return "limit has been set"

    if (int(getlimit)==-1):
        return "you are rate limited"
    else:
        redisConnect.hincrby(userid, 'limit', -1)
