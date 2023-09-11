from zjson import AsyncClient

db = AsyncClient("file.json")

async def main():
    # await db.set("hi", 1)
    print([key async for key in db.keys()])
    print(db.path)

db.run(main())
