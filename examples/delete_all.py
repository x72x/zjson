from zjson import AsyncClient

db = AsyncClient("file.json")

async def main():
    await db.delall()

db.run(main())
