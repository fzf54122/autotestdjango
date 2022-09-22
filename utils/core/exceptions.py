

class ParamException(Exception):
    def ___init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        return f"params invalid!! *args: tuple = *{self._args}, **kwargs: dict = **{self._kwargs})"
