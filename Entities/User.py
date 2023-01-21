from datetime import datetime


class User:
    id: int
    url: str
    email: str
    password:str
    last_updated: datetime
    model_url: str