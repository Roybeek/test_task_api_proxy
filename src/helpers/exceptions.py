class BadRequest(Exception):
    def __init__(self, msg: str, status_code: int = 400):
        super().__init__(f"Ошибка запроса - {msg}")
        self.status_code = status_code
