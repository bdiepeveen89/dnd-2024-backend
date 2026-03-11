from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "player"

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    class Config: from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ─── Characters ───────────────────────────────────────────────────────────────
class CharacterCreate(BaseModel):
    name: str
    race: str
    class_name: str
    background: Optional[str] = None
    alignment: Optional[str] = None
    level: int = 1
    hp: int
    max_hp: int
    ac: int = 10
    str_score: int = 10
    dex_score: int = 10
    con_score: int = 10
    int_score: int = 10
    wis_score: int = 10
    cha_score: int = 10
    spells_json: Optional[List[Any]] = None
    portrait_path: Optional[str] = None
    campaign_id: Optional[int] = None

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    hp: Optional[int] = None
    max_hp: Optional[int] = None
    xp: Optional[int] = None
    ac: Optional[int] = None
    notes: Optional[str] = None
    spells_json: Optional[List[Any]] = None
    inventory_json: Optional[List[Any]] = None
    portrait_path: Optional[str] = None

class CharacterOut(BaseModel):
    id: int
    name: str
    race: str
    class_: str
    background: Optional[str]
    alignment: Optional[str]
    level: int
    xp: int
    hp: int
    max_hp: int
    ac: int
    str_score: int
    dex_score: int
    con_score: int
    int_score: int
    wis_score: int
    cha_score: int
    portrait_path: Optional[str]
    spells_json: Optional[List[Any]]
    created_at: datetime
    class Config: from_attributes = True


# ─── Campaigns ────────────────────────────────────────────────────────────────
class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    setting: Optional[str] = None

class CampaignOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    setting: Optional[str]
    status: str
    created_at: datetime
    class Config: from_attributes = True


# ─── Notes ────────────────────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    title: Optional[str] = None
    content: str
    note_type: str = "general"
    session_num: Optional[int] = None
    is_private: bool = False

class NoteOut(BaseModel):
    id: int
    title: Optional[str]
    content: str
    note_type: str
    session_num: Optional[int]
    is_private: bool
    created_at: datetime
    class Config: from_attributes = True


# ─── Loot ─────────────────────────────────────────────────────────────────────
class LootCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 1
    value_gp: float = 0
    item_type: Optional[str] = None
    found_at: Optional[str] = None

class LootOut(BaseModel):
    id: int
    name: str
    quantity: int
    value_gp: float
    item_type: Optional[str]
    found_at: Optional[str]
    class Config: from_attributes = True


# ─── Homebrew ─────────────────────────────────────────────────────────────────
class HomebrewCreate(BaseModel):
    brew_type: str
    name: str
    data_json: Any
    is_public: bool = False

class HomebrewOut(BaseModel):
    id: int
    brew_type: str
    name: str
    data_json: Any
    is_public: bool
    created_at: datetime
    class Config: from_attributes = True
