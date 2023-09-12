from zjson import AsyncClient

db = AsyncClient("file.json", auto_clean_and_backup=True)

async def main():
    print(await db.get("hi"))
    await db.set("i", 2)

db.run(main())
