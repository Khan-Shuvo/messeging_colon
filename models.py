from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    email: str
    password: str
    is_online: bool
    last_seen: datetime

@dataclass
class Message:
    id: int
    sender_id: int
    receiver_id: int = None
    group_id: int = None
    content: str = ""
    timestamp: datetime = None
    is_read: bool = False

@dataclass
class Group:
    id: int
    name: str
    created_by: int
    created_at: datetime = None