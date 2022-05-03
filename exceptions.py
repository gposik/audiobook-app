class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


class APIError(Exception):
    def __init__(self, status_code, title, messages, data, valid_data):
        Exception.__init__(self)
        self.status_code = status_code
        self.title = title
        self.messages = messages
        self.data = data
        self.valid_data = valid_data

    def to_dict(self):
        return dict(
            status=self.status_code,
            title=self.title,
            messages=self.messages,
            data=self.data,
            valid_data=self.valid_data,
        )
