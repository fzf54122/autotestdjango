from abc import abstractmethod, ABC


NUMBERS = [chr(i) for i in range(48, 58)]
ALPHABET = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
CHAOS = NUMBERS + ALPHABET
CHARSET = [chr(i) for i in range(256)]


class ICipher(ABC):

    @abstractmethod
    def encrypt(self, data):
        ...

    @abstractmethod
    def decrypt(self, data):
        ...
