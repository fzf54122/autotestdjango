import unittest


class TestLoader(unittest.TestLoader):
    
    def __init__(self):
        super().__init__()

    def load_from_path(self, path):
        ...
