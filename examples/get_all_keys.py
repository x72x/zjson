from zjson import AsyncClient

app = AsyncClient("file.json")

async def main():
    # await app.set("hi", 1)
    print([key async for key in app.keys()])
    print(app.path)

app.run(main())
