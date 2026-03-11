"""
D&D 2024 API - FastAPI Backend
Endpoints: Auth, Characters, Campaigns, Spells, Spell Images (PDF extract), Homebrew
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager
from typing import Optional
import os
import time
import logging

from database import engine, Base, get_db
import models, schemas, auth, crud
from spell_image_extractor import SpellImageExtractor

logger = logging.getLogger("uvicorn.error")


def wait_for_db(retries: int = 15, delay: float = 3.0):
    """Wacht totdat MySQL bereikbaar is en maak dan de tabellen aan."""
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database verbinding OK — tabellen aangemaakt/geverifieerd.")
            return
        except OperationalError as e:
            logger.warning(f"⏳ DB nog niet klaar (poging {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)
    raise RuntimeError("❌ Kon na meerdere pogingen geen verbinding maken met de database.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    yield

# ─── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="D&D 2024 API",
    description="Backend voor D&D 2024 Character Manager, Campaign Tracker en Spell Image Extractor",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In productie: stel je domein in
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploads as static files
os.makedirs("uploads", exist_ok=True)
os.makedirs("spell_images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/spell_images", StaticFiles(directory="spell_images"), name="spell_images")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ─── Dependency: current user ─────────────────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return auth.verify_token(token, db)


# ─── AUTH ─────────────────────────────────────────────────────────────────────
@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Ongeldige inloggegevens")
    token = auth.create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": schemas.UserOut.from_orm(user)}


@app.post("/api/auth/register", response_model=schemas.UserOut)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(400, "E-mail al in gebruik")
    return crud.create_user(db, data)


# ─── CHARACTERS ───────────────────────────────────────────────────────────────
@app.get("/api/characters", response_model=list[schemas.CharacterOut])
def list_characters(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_characters(db, user.id)


@app.post("/api/characters", response_model=schemas.CharacterOut)
def create_character(data: schemas.CharacterCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_character(db, data, user.id)


@app.get("/api/characters/{char_id}", response_model=schemas.CharacterOut)
def get_character(char_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    char = crud.get_character(db, char_id, user.id)
    if not char:
        raise HTTPException(404, "Karakter niet gevonden")
    return char


@app.put("/api/characters/{char_id}", response_model=schemas.CharacterOut)
def update_character(char_id: int, data: schemas.CharacterUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    char = crud.update_character(db, char_id, data, user.id)
    if not char:
        raise HTTPException(404, "Karakter niet gevonden")
    return char


@app.delete("/api/characters/{char_id}")
def delete_character(char_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    crud.delete_character(db, char_id, user.id)
    return {"ok": True}


@app.post("/api/characters/{char_id}/portrait")
async def upload_portrait(
    char_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Upload een portretafbeelding voor een karakter."""
    char = crud.get_character(db, char_id, user.id)
    if not char:
        raise HTTPException(404, "Karakter niet gevonden")

    # Validate image
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Alleen afbeeldingen toegestaan")

    # Save file
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
    filename = f"portrait_{char_id}_{user.id}.{ext}"
    path = f"uploads/{filename}"

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Bestand te groot (max 5MB)")

    with open(path, "wb") as f:
        f.write(content)

    char.portrait_path = f"/uploads/{filename}"
    db.commit()
    return {"portrait_url": char.portrait_path}


# ─── CAMPAIGNS ────────────────────────────────────────────────────────────────
@app.get("/api/campaigns", response_model=list[schemas.CampaignOut])
def list_campaigns(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_campaigns(db, user.id)


@app.post("/api/campaigns", response_model=schemas.CampaignOut)
def create_campaign(data: schemas.CampaignCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_campaign(db, data, user.id)


@app.get("/api/campaigns/{camp_id}/notes", response_model=list[schemas.NoteOut])
def get_notes(camp_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_notes(db, camp_id, user.id)


@app.post("/api/campaigns/{camp_id}/notes", response_model=schemas.NoteOut)
def add_note(camp_id: int, data: schemas.NoteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_note(db, camp_id, data, user.id)


@app.get("/api/campaigns/{camp_id}/loot", response_model=list[schemas.LootOut])
def get_loot(camp_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_loot(db, camp_id)


@app.post("/api/campaigns/{camp_id}/loot", response_model=schemas.LootOut)
def add_loot(camp_id: int, data: schemas.LootCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_loot(db, camp_id, data)


# ─── SPELL IMAGES (PDF Extractor) ─────────────────────────────────────────────
@app.post("/api/spells/extract-images")
async def extract_spell_images(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Upload een D&D PDF bronboek. De API zoekt automatisch naar spellenamen
    op pagina's en knipt de bijbehorende illustraties uit.
    Vereist DM-rol.
    """
    if user.role not in ("dm", "admin"):
        raise HTTPException(403, "Alleen DM's kunnen spell images extraheren")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Upload een PDF bestand")

    # Save PDF temporarily
    pdf_path = f"pdfs/{file.filename}"
    content = await file.read()
    with open(pdf_path, "wb") as f:
        f.write(content)

    # Extract images
    extractor = SpellImageExtractor()
    results = extractor.extract_from_pdf(pdf_path, output_dir="spell_images")

    # Save to DB
    saved = []
    for spell_name, image_path in results.items():
        existing = db.query(models.SpellImage).filter_by(spell_name=spell_name).first()
        if existing:
            existing.image_path = image_path
        else:
            db.add(models.SpellImage(
                spell_name=spell_name,
                image_path=image_path,
                source_book=file.filename
            ))
        saved.append(spell_name)
    db.commit()

    return {"extracted": len(saved), "spells": saved}


@app.get("/api/spells/images")
def get_spell_images(db: Session = Depends(get_db)):
    """Geeft een mapping van spellenaam -> image URL terug."""
    images = db.query(models.SpellImage).all()
    return {img.spell_name: f"/spell_images/{os.path.basename(img.image_path)}" for img in images}


@app.get("/api/spells/image/{spell_name}")
def get_spell_image(spell_name: str, db: Session = Depends(get_db)):
    img = db.query(models.SpellImage).filter_by(spell_name=spell_name).first()
    if not img:
        raise HTTPException(404, "Geen afbeelding gevonden voor deze spreuk")
    return {"spell": spell_name, "image_url": f"/spell_images/{os.path.basename(img.image_path)}"}


# ─── HOMEBREW ─────────────────────────────────────────────────────────────────
@app.get("/api/homebrew", response_model=list[schemas.HomebrewOut])
def list_homebrew(brew_type: Optional[str] = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_homebrew(db, user.id, brew_type)


@app.post("/api/homebrew", response_model=schemas.HomebrewOut)
def create_homebrew(data: schemas.HomebrewCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_homebrew(db, data, user.id)


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
