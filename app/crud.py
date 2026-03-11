from sqlalchemy.orm import Session
import models, schemas, auth


# ─── Users ────────────────────────────────────────────────────────────────────
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserCreate):
    user = models.User(
        username=data.username,
        email=data.email,
        password_hash=auth.hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ─── Characters ───────────────────────────────────────────────────────────────
def get_characters(db: Session, owner_id: int):
    return db.query(models.Character).filter(models.Character.owner_id == owner_id).all()


def get_character(db: Session, char_id: int, owner_id: int):
    return db.query(models.Character).filter(
        models.Character.id == char_id,
        models.Character.owner_id == owner_id
    ).first()


def create_character(db: Session, data: schemas.CharacterCreate, owner_id: int):
    char = models.Character(
        owner_id=owner_id,
        name=data.name,
        race=data.race,
        class_=data.class_name,
        background=data.background,
        alignment=data.alignment,
        level=data.level,
        hp=data.hp,
        max_hp=data.max_hp,
        ac=data.ac,
        str_score=data.str_score,
        dex_score=data.dex_score,
        con_score=data.con_score,
        int_score=data.int_score,
        wis_score=data.wis_score,
        cha_score=data.cha_score,
        spells_json=data.spells_json,
        portrait_path=data.portrait_path,
        campaign_id=data.campaign_id
    )
    db.add(char)
    db.commit()
    db.refresh(char)
    return char


def update_character(db: Session, char_id: int, data: schemas.CharacterUpdate, owner_id: int):
    char = get_character(db, char_id, owner_id)
    if not char:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(char, field, value)
    db.commit()
    db.refresh(char)
    return char


def delete_character(db: Session, char_id: int, owner_id: int):
    char = get_character(db, char_id, owner_id)
    if char:
        db.delete(char)
        db.commit()


# ─── Campaigns ────────────────────────────────────────────────────────────────
def get_campaigns(db: Session, user_id: int):
    return db.query(models.Campaign).filter(models.Campaign.dm_id == user_id).all()


def create_campaign(db: Session, data: schemas.CampaignCreate, dm_id: int):
    camp = models.Campaign(
        name=data.name,
        description=data.description,
        setting=data.setting,
        dm_id=dm_id
    )
    db.add(camp)
    db.commit()
    db.refresh(camp)
    return camp


# ─── Notes ────────────────────────────────────────────────────────────────────
def get_notes(db: Session, campaign_id: int, user_id: int):
    return db.query(models.CampaignNote).filter(
        models.CampaignNote.campaign_id == campaign_id
    ).all()


def create_note(db: Session, campaign_id: int, data: schemas.NoteCreate, author_id: int):
    note = models.CampaignNote(
        campaign_id=campaign_id,
        author_id=author_id,
        title=data.title,
        content=data.content,
        note_type=data.note_type,
        session_num=data.session_num,
        is_private=data.is_private
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


# ─── Loot ─────────────────────────────────────────────────────────────────────
def get_loot(db: Session, campaign_id: int):
    return db.query(models.Loot).filter(models.Loot.campaign_id == campaign_id).all()


def create_loot(db: Session, campaign_id: int, data: schemas.LootCreate):
    item = models.Loot(
        campaign_id=campaign_id,
        name=data.name,
        description=data.description,
        quantity=data.quantity,
        value_gp=data.value_gp,
        item_type=data.item_type,
        found_at=data.found_at
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ─── Homebrew ─────────────────────────────────────────────────────────────────
def get_homebrew(db: Session, user_id: int, brew_type: str = None):
    q = db.query(models.Homebrew).filter(
        (models.Homebrew.creator_id == user_id) | (models.Homebrew.is_public == True)
    )
    if brew_type:
        q = q.filter(models.Homebrew.brew_type == brew_type)
    return q.all()


def create_homebrew(db: Session, data: schemas.HomebrewCreate, creator_id: int):
    brew = models.Homebrew(
        creator_id=creator_id,
        brew_type=data.brew_type,
        name=data.name,
        data_json=data.data_json,
        is_public=data.is_public
    )
    db.add(brew)
    db.commit()
    db.refresh(brew)
    return brew
