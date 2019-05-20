class SomethingWrong(Exception):
    def __init__(self, message='Something wrong'):
        self.message = message


class BadRequest(SomethingWrong):
    def __init__(self, message='Bad Request'):
        self.message = message


class NotFound(SomethingWrong):
    def __init__(self, message='Not Found'):
        self.message = message
