<p align="center">
    <a href="https://github.com/x72x/zjson/">
        <img src="https://dev-zaiddev.pantheonsite.io/zaid/files/AgACAgIAAxkBAAILyWT_j6PAbt8P3F1JiqznohMs.jpg" alt="zjson" width="256">
    </a>
    <br>
    <b>Json Database full async</b>
    <br>
    <a href="https://github.com/x72x/zjson/tree/main/examples">
        Examples
    </a>
    •
    <a href="https://t.me/Y88F8">
        News
    </a>
</p>

## Aio-Json

> Example

``` python
from zjson import AsyncClient

db = AsyncClient(name="db.json", directory="cache")

async def main():
    await db.set(
        key="key",
        value="value"
    )
    print(await db.get("key")) # value
    await db.set(
        key="key2",
        value=[1, 2, 3],
        expire=10 # expire after 10 seconds
    )
    await db.sleep(10)
    print(await db.get("key2")) # None

db.run(main())

```

### Installing

``` bash
pip3 install -U zjson
```

### Community

- Join the telegram channel: https://t.me/Y88F8
