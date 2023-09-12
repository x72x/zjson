# from .object import Object

# class SyncClient(Object):
#     def __init__(self, name: str, directory: str = None, indent = 4, auto_clean_and_backup: bool = None) -> None:
#         """
#         Args:

#             name (str): Name of database file

#             directory (str, optional): Path to work dir. Defaults to None.

#             indent (int, optional): indent in file dump. Defaults to 4.

#             auto_clean_and_backup (bool, optional): Auto remove expired keys and create data backup into file. Defaults to None.


#         Raises:
#             zjson.errors.FileAlreadyConnected: When you use same file more than one time
#         """
#         super().__init__()
#         self.name = name
#         self.directory = directory
#         self.path = self.directory+"/"+self.name if self.directory else self.name
#         self.indent = indent
#         self.auto_clean_and_backup = auto_clean_and_backup
