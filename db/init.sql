-- D&D 2024 Database Schema
-- Run automatically on first start via docker-entrypoint-initdb.d

USE dnd2024;

-- ─── Users ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role        ENUM('dm', 'player', 'admin') DEFAULT 'player',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login  DATETIME
);

-- Default users (passwords: dungeon123 / player123)
INSERT IGNORE INTO users (username, email, password_hash, role) VALUES
('dm',     'dm@dnd2024.local',     '$2b$12$GkOy/O2RN.PxWjlGi/T4COvUEsHWqEMhIxPaRRGgQfcT8t7bPUSEi', 'dm'),
('player', 'player@dnd2024.local', '$2b$12$zBo/mV3u6fW2p5tRCXK5QO4PO4h2vVjRhWjGT7XWXCbvqe4oLvuQq', 'player');

-- ─── Campaigns ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaigns (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    dm_id       INT NOT NULL,
    setting     VARCHAR(100),
    status      ENUM('active', 'paused', 'completed') DEFAULT 'active',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dm_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Characters ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS characters (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    owner_id        INT NOT NULL,
    campaign_id     INT,
    name            VARCHAR(100) NOT NULL,
    race            VARCHAR(50) NOT NULL,
    class           VARCHAR(50) NOT NULL,
    background      VARCHAR(50),
    alignment       VARCHAR(30),
    level           INT DEFAULT 1,
    xp              INT DEFAULT 0,
    hp              INT NOT NULL,
    max_hp          INT NOT NULL,
    ac              INT DEFAULT 10,
    proficiency_bonus INT DEFAULT 2,
    -- Ability scores
    str_score       INT DEFAULT 10,
    dex_score       INT DEFAULT 10,
    con_score       INT DEFAULT 10,
    int_score       INT DEFAULT 10,
    wis_score       INT DEFAULT 10,
    cha_score       INT DEFAULT 10,
    -- Extra
    portrait_path   VARCHAR(255),
    notes           TEXT,
    spells_json     JSON,
    inventory_json  JSON,
    traits_json     JSON,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

-- ─── Campaign Notes ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaign_notes (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    author_id   INT NOT NULL,
    title       VARCHAR(200),
    content     TEXT NOT NULL,
    note_type   ENUM('session', 'lore', 'npc', 'location', 'quest', 'general') DEFAULT 'general',
    session_num INT,
    is_private  BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Loot / Inventory ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS loot (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    quantity    INT DEFAULT 1,
    value_gp    DECIMAL(10,2) DEFAULT 0,
    item_type   VARCHAR(50),
    assigned_to INT,
    found_at    VARCHAR(100),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES characters(id) ON DELETE SET NULL
);

-- ─── Party Members ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS party_members (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    user_id     INT,
    character_id INT,
    invite_email VARCHAR(120),
    invite_status ENUM('pending','accepted','declined') DEFAULT 'pending',
    joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE SET NULL
);

-- ─── Homebrew ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS homebrew (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    creator_id  INT NOT NULL,
    brew_type   ENUM('race', 'class', 'spell', 'monster', 'item', 'background') NOT NULL,
    name        VARCHAR(100) NOT NULL,
    data_json   JSON NOT NULL,
    is_public   BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Spell Images (extracted from PDFs) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS spell_images (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    spell_name  VARCHAR(100) NOT NULL UNIQUE,
    image_path  VARCHAR(255) NOT NULL,
    source_book VARCHAR(100),
    page_num    INT,
    extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
