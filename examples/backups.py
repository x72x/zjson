from zjson import AsyncClient

db = AsyncClient("file.json")
# db.data_from_backup("file.json-backup")

async def main():
    await db.get_backup("file.json-backup")

db.run(main())
