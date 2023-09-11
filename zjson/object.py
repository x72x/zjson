from json import dumps

class Object:
    def __init__(self):
        pass

    @staticmethod
    def __default__(obj: "Object"):
        return {
            "class_name": obj.__class__.__name__,
            **{
                attr: (
                    getattr(obj, attr)
                )
                for attr in obj.__dict__
                if getattr(obj, attr) is not None
            }
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=Object.__default__, ensure_ascii=False)

