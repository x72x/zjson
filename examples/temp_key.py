from zjson import AsyncClient

db = AsyncClient("file.json")

async def main():
    await db.set("hi", 1, expire=5)
    await db.sleep(await db.ttl("hi"))
    print(await db.get("hi")) # None
  
db.run(main())
