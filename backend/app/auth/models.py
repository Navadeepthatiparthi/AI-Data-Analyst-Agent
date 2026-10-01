from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    full_name: str
    created_at: datetime