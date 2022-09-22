from abc import ABC, abstractmethod


class StatusCodeException(Exception):

    def __init__(self, status_code):
        self.message = 'Status code invalid'
        self.status_code = status_code

    def __str__(self):
        return f"{self.message}: {self.status_code}"


class ResponseContentException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class AuthorizationException(Exception):

    def __init__(self, token=None, require_login=None, message=None):
        self.token = token
        self.require_login = require_login
        self.message = message

    def __str__(self):
        if not self.message:
            return f"CurrentToken: {self.token} with require_login set {self.require_login}, Please Login first."
        else:
            return self.message


class ParamException(Exception):
    def ___init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        return f"params invalid!! *args: tuple = *{self._args}, **kwargs: dict = **{self._kwargs})"
