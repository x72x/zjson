import asyncio
import aiofiles
import datetime
import json
import os


from re import search
from typing import Any, AsyncGenerator, Union

from .object import Object
from .errors import FileAlreadyConnected

_names = []
_cache = {}
_lock = asyncio.Lock()



class AsyncClient(Object):
    def __init__(self, name: str, directory: str = None, indent = 4, auto_clean_and_backup: bool = None) -> None:
        """
        Args:

            name (str): Name of database file

            directory (str, optional): Path to work dir. Defaults to None.

            indent (int, optional): indent in file dump. Defaults to 4.

            auto_clean_and_backup (bool, optional): Auto remove expired keys and create data backup into file. Defaults to None.


        Raises:
            zjson.errors.FileAlreadyConnected: When you use same file more than one time
        """
        super().__init__()
        self.name = name
        self.directory = directory
        self.path = self.directory+"/"+self.name if self.directory else self.name
        self.indent = indent
        self.auto_clean_and_backup = auto_clean_and_backup

        if self.path in _names:
            raise FileAlreadyConnected(f"File [ {self.path} ] Already Connected")

        self._repair()
        if self.path not in _names:
            _names.append(self.path)

        if self.auto_clean_and_backup:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            loop.create_task(_clean(self))

    def _repair(self):
        if (self.directory) and (not os.path.isdir(self.directory)):
            os.mkdir(self.directory)
            with open(self.path, 'w+') as f:
                data = {'all': {}, 'expires': {}}
                f.write(json.dumps(data, indent=self.indent, ensure_ascii=False))

        if (not self.directory) and (not os.path.exists(self.name)):
            with open(self.path, 'w+') as f:
                data = {'all': {}, 'expires': {}}
                f.write(json.dumps(data, indent=self.indent, ensure_ascii=False))

        if (self.directory) and (not os.path.exists(self.path)):
            with open(self.path, 'w+') as f:
                data = {'all': {}, 'expires': {}}
                f.write(json.dumps(data, indent=self.indent, ensure_ascii=False))

        try:
            with open(self.path, 'r') as f:
                json.loads(f.read())
        except:
            with open(self.path, 'w+') as f:
                data = {'all': {}, 'expires': {}}
                f.write(json.dumps(data, indent=self.indent, ensure_ascii=False))

    def data_from_backup(self, path: str):
        """
        Args:
            path (str): Path for output file
        """
        with open(path, 'r') as f:
            data = f.read()
        with open(self.path, 'w+') as f:
            f.write(data)


    async def _read(self) -> dict:
        if _cache:
            return _cache["cache"]
        async with aiofiles.open(self.path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.loads(await f.read())
            _cache["cache"]=data
            return data

    async def _update(self, data: dict):
        async with aiofiles.open(self.path, 'w+', encoding='utf-8', errors='ignore') as f:
            await f.write(json.dumps(data, indent=self.indent, ensure_ascii=False))

    async def set(
        self,
        key: "str",
        value: Union["str", "int", "list", "dict", "float", "bool", "None", "set"],
        expire: "int" = None
    ) -> Any:
        """
        Args:
            key (str): Key name .
            value (Union[&quot;str&quot;, &quot;int&quot;, &quot;list&quot;, &quot;dict&quot;, &quot;float&quot;, &quot;bool&quot;, &quot;None&quot;, &quot;set&quot;]): Value .
            expire (int, optional): This key will be expired after specific seconds. Defaults to None.

        Raises:
            TypeError: When value type not supported

        Returns:
            Any: Key data
        """
        if (value).__class__.__name__ not in {"str", "int", "list", "dict", "float", "bool", "NoneType", "set"}:
            raise TypeError(f"Unsopported type [ {value.__class__.__name__} ]")
        if (value).__class__.__name__ == "set": value = [i for i in value]
        data = await self._read()
        async with aiofiles.open(self.path, 'w+', encoding='utf-8') as f:
            if expire:
                if data["all"].get(key): del data["all"][key]
                r = {"value": value, "expire_stamp": (datetime.datetime.now() + datetime.timedelta(seconds=expire)).timestamp()}
                data["expires"][key]=r
            else:
                if data["expires"].get(key): del data["expires"][key]
                r = value
                data["all"][key]=r
                # print(data)
                # print(json.dumps(data, indent=self.indent, ensure_ascii=False, sort_keys=True, default=data))
        await self._update(data)
        return r

    async def get(
        self,
        key: "str"
    ):
        """
        Args:
            key (str): Key Name
        Returns:
            Any: Value of the key or NoneType
        """
        data = await self._read()
        all = data["all"]
        expires = data["expires"]
        if all.get(key, None) is not None:
            return data["all"][key]
        elif expires.get(key, None) is not None:
            # return data["expires"][key]["value"]
            if datetime.datetime.now() > datetime.datetime.fromtimestamp(data["expires"][key]["expire_stamp"]):
                del data["expires"][key]
                return None
            else:
                return data["expires"][key]["value"]
        else:
            return None

    async def ttl(
        self,
        key: "str"
    ):
        """
        Args:
            key (str): Key name

        Returns:
            float: time in float to expire the key or None if the key is not expiring key
        """
        data = await self._read()
        expires = data["expires"]
        if expires.get(key, None) is not None:
            if datetime.datetime.now() > datetime.datetime.fromtimestamp(data["expires"][key]["expire_stamp"]):
                return None
            return data["expires"][key]["expire_stamp"] - datetime.datetime.now().timestamp()
        return None

    async def delete(
        self,
        key: "str"
    ):
        """
        Args:
            key (str): Key name
        """
        data = await self._read()
        all = data.get("all")
        expires = data.get("expires")
        if (all) and (key in all):
            del data["all"][key]
        if (expires) and (key in expires):
            del data["expires"][key]
        await self._update(data)
        return True


    async def delall(self) -> bool:
        del _cache["cache"]
        async with aiofiles.open(self.path, 'w+', encoding='utf-8') as f:
            await f.write(json.dumps({'all': {}, 'expires': {}}, indent=self.indent, ensure_ascii=False))
        return True

    async def keys(self, pattern: str = None, limit: int = 0) -> AsyncGenerator["str", None]:
        """
        Args:
            pattern (str): regex patern
            limit (int): keys limit
        Yields:
            str: Name of the key
        """
        data = await self._read()
        all = data.get("all")
        expires = data.get("expires")
        count = 0
        if all:
            for i in all:
                if (limit) and (count == limit): break
                if (pattern) and (search(pattern, i)):
                    count += 1
                    yield i
                elif not pattern:
                    count += 1
                    yield i
        if expires:
            for i in expires:
                if (limit) and (count == limit): break
                if (pattern) and (search(pattern, i)):
                    count += 1
                    yield i
                elif not pattern:
                    count += 1
                    yield i

    async def get_backup(self, file_name: str = None) -> str:
        """_summary_

        Args:
            file_name (str, optional): Output of the backup file. Defaults to None.

        Returns:
            str: file path
        """
        file_name = file_name if file_name else self.path+"-backup"
        data = await self._read()
        async with aiofiles.open(file_name, 'w+') as f:
            await f.write(json.dumps(data, indent=4, ensure_ascii=False))
        return file_name

    async def sleep(self, _t: Union["int", "float"]):
        """
        Args:
            _t (Union[&quot;int&quot;, &quot;float&quot;]): Time to sleep

        same as &quot;await asyncio.sleep()&quot;
        """
        await asyncio.sleep(_t)


    def run(
        self,
        coroutine=None
    ):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        run = loop.run_until_complete
        if coroutine:
            run(coroutine)

async def __clean(c: AsyncClient):
    try:
        if _cache:
            await c.get_backup()
            data = _cache["cache"]
            keys = data["expires"]
            for i in keys:
                if datetime.datetime.now() >= datetime.datetime.fromtimestamp(keys[i]['expire_stamp']):
                    del data['expires'][i]
                    _cache["cache"]=data
            await c._update(data)
        else:
            await c._read()
    except:
        try:
            await c._update(data)
        except:
            pass

async def _clean(c: AsyncClient):
    while True:
        async with _lock:
            await __clean(c)


