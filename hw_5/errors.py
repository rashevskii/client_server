class IncorrectDataRecivedError(Exception):
    def __str__(self):
        return 'Get incorrect message.'


class NonDictInputError(Exception):
    def __str__(self):
        return 'Argument must be type of dict.'


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Missing a required field {self.missing_field}.'
