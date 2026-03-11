# D&D 2024 Backend — Docker + Python + MySQL

## Vereisten
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) geïnstalleerd
- De `dnd-app/` map staat op hetzelfde niveau als `dnd-backend/`

## Starten

```bash
cd dnd-backend
docker compose up --build
```

Dit start automatisch:
| Container | Poort | Wat |
|-----------|-------|-----|
| `dnd_db`    | 3306 | MySQL 8.3 database |
| `dnd_api`   | 8000 | FastAPI backend |
| `dnd_nginx` | 80   | Nginx → frontend + API proxy |

## Gebruik

- **App openen:** http://localhost
- **API documentatie:** http://localhost/api/docs
- **Direct API:** http://localhost:8000/api/docs

### Standaard inloggegevens
| Gebruiker | Wachtwoord | Rol |
|-----------|------------|-----|
| `dm`      | `dungeon123` | DM |
| `player`  | `player123`  | Speler |

## Spell Images extraheren uit PDF

1. Log in als DM
2. Ga naar `POST /api/spells/extract-images` in de API docs
3. Upload één van de D&D PDF bronboeken (PHB 2024, MM 2024, etc.)
4. De API scant de PDF, vindt spellenamen, knipt de bijbehorende afbeeldingen eruit
5. Afbeeldingen worden opgeslagen in de `spell_images/` volume
6. De frontend haalt automatisch de images op via `/api/spells/images`

## Map-structuur

```
dnd-backend/
├── docker-compose.yml
├── nginx.conf
├── README.md
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # SQLAlchemy database modellen
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py              # Database operaties
│   ├── auth.py              # JWT authenticatie + bcrypt
│   ├── database.py          # DB verbinding
│   └── spell_image_extractor.py  # PyMuPDF spell image extractor
└── db/
    └── init.sql             # Database schema + default users
```

## Stoppen & data bewaren

```bash
docker compose down        # stop containers, data blijft bewaard
docker compose down -v     # stop + verwijder alle data (reset)
```

=======
# DnD2024-App
DnD Character creation and DM tool
