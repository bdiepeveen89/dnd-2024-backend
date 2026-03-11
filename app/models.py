from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("dm", "player", "admin"), default="player")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    characters = relationship("Character", back_populates="owner")
    campaigns = relationship("Campaign", back_populates="dm")


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    dm_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    setting = Column(String(100), nullable=True)
    status = Column(Enum("active", "paused", "completed"), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    dm = relationship("User", back_populates="campaigns")
    notes = relationship("CampaignNote", back_populates="campaign")
    loot = relationship("Loot", back_populates="campaign")


class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    class_ = Column("class", String(50), nullable=False)
    background = Column(String(50), nullable=True)
    alignment = Column(String(30), nullable=True)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    ac = Column(Integer, default=10)
    proficiency_bonus = Column(Integer, default=2)
    str_score = Column(Integer, default=10)
    dex_score = Column(Integer, default=10)
    con_score = Column(Integer, default=10)
    int_score = Column(Integer, default=10)
    wis_score = Column(Integer, default=10)
    cha_score = Column(Integer, default=10)
    portrait_path = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    spells_json = Column(JSON, nullable=True)
    inventory_json = Column(JSON, nullable=True)
    traits_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", back_populates="characters")


class CampaignNote(Base):
    __tablename__ = "campaign_notes"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    note_type = Column(Enum("session", "lore", "npc", "location", "quest", "general"), default="general")
    session_num = Column(Integer, nullable=True)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="notes")


class Loot(Base):
    __tablename__ = "loot"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    value_gp = Column(DECIMAL(10, 2), default=0)
    item_type = Column(String(50), nullable=True)
    assigned_to = Column(Integer, ForeignKey("characters.id"), nullable=True)
    found_at = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="loot")


class Homebrew(Base):
    __tablename__ = "homebrew"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brew_type = Column(Enum("race", "class", "spell", "monster", "item", "background"), nullable=False)
    name = Column(String(100), nullable=False)
    data_json = Column(JSON, nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SpellImage(Base):
    __tablename__ = "spell_images"
    id = Column(Integer, primary_key=True, index=True)
    spell_name = Column(String(100), unique=True, nullable=False)
    image_path = Column(String(255), nullable=False)
    source_book = Column(String(100), nullable=True)
    page_num = Column(Integer, nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow)
