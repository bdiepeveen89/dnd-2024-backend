"""
Spell Image Extractor
Gebruikt PyMuPDF om D&D bronboeken te scannen op spellenamen
en snijdt de bijbehorende afbeeldingen eruit.
"""
import fitz  # PyMuPDF
import os
import re
from pathlib import Path


# Bekende D&D 2024 spellenamen (subset - wordt uitgebreid via DB)
KNOWN_SPELLS = {
    "Fireball", "Lightning Bolt", "Magic Missile", "Cure Wounds", "Healing Word",
    "Mage Armor", "Invisibility", "Fly", "Haste", "Slow", "Counterspell",
    "Dispel Magic", "Misty Step", "Dimension Door", "Teleport",
    "Acid Arrow", "Burning Hands", "Cone of Cold", "Chain Lightning",
    "Cloudkill", "Darkness", "Darkness", "Detect Magic", "Disintegrate",
    "Dominate Person", "Faerie Fire", "Fear", "Feather Fall", "Fireball",
    "Flame Strike", "Freedom of Movement", "Gaseous Form",
    "Globe of Invulnerability", "Guiding Bolt", "Hold Monster", "Hold Person",
    "Hunger of Hadar", "Hypnotic Pattern", "Ice Storm", "Inflict Wounds",
    "Knock", "Levitate", "Maze", "Moonbeam", "Polymorph", "Prayer of Healing",
    "Raise Dead", "Revivify", "Sacred Flame", "Scorching Ray", "Shatter",
    "Shield", "Silence", "Sleep", "Spiritual Weapon", "Stone Shape",
    "Stoneskin", "Sunbeam", "Sunburst", "Thunderwave", "Time Stop",
    "Toll the Dead", "Wall of Fire", "Wall of Force", "Wish",
    # Cantrips
    "Eldritch Blast", "Fire Bolt", "Ray of Frost", "Shocking Grasp",
    "Chill Touch", "Mage Hand", "Minor Illusion", "Prestidigitation",
    "Guidance", "Sacred Flame", "Spare the Dying", "Word of Radiance",
    "Dancing Lights", "True Strike", "Blade Ward", "Vicious Mockery",
    "Produce Flame",
}


class SpellImageExtractor:
    """
    Scant PDF pagina's op spellenamen en extraheert nabijgelegen afbeeldingen.
    Strategie:
    1. Scan elke pagina op bekende spellenamen in de tekst
    2. Als gevonden: zoek naar afbeeldingsblokken op die pagina
    3. Sla de grootste/relevantste afbeelding op als spell-artwork
    """

    def __init__(self, extra_spells: set = None):
        self.spells = KNOWN_SPELLS.copy()
        if extra_spells:
            self.spells.update(extra_spells)

    def extract_from_pdf(self, pdf_path: str, output_dir: str = "spell_images") -> dict:
        """
        Verwerk een PDF en extraheer spell-afbeeldingen.
        Returns: {spell_name: saved_image_path}
        """
        os.makedirs(output_dir, exist_ok=True)
        results = {}

        doc = fitz.open(pdf_path)
        book_name = Path(pdf_path).stem

        print(f"Verwerking {pdf_path}: {len(doc)} pagina's")

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            # Zoek spellenamen op deze pagina
            found_spells = self._find_spells_on_page(text)
            if not found_spells:
                continue

            # Zoek afbeeldingen op deze pagina
            images = self._get_page_images(doc, page, page_num)
            if not images:
                continue

            # Koppel elke gevonden spell aan de beste afbeelding
            for spell_name in found_spells:
                if spell_name in results:
                    continue  # al gevonden

                # Kies de grootste afbeelding als primaire artwork
                best_image = max(images, key=lambda img: img['width'] * img['height'])

                save_path = self._save_image(
                    doc, best_image, output_dir, spell_name, book_name, page_num
                )
                if save_path:
                    results[spell_name] = save_path
                    print(f"  ✓ {spell_name} → {save_path}")

        doc.close()
        print(f"Klaar: {len(results)} spell-afbeeldingen gevonden")
        return results

    def _find_spells_on_page(self, text: str) -> list:
        """Zoek bekende spellenamen in paginatekst."""
        found = []
        text_lower = text.lower()
        for spell in self.spells:
            # Zoek als header/titel (bijv. gevolgd door newline of school-naam)
            pattern = r'\b' + re.escape(spell.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found.append(spell)
        return found

    def _get_page_images(self, doc: fitz.Document, page: fitz.Page, page_num: int) -> list:
        """Haal alle afbeeldingen op van een pagina met hun afmetingen."""
        images = []
        image_list = page.get_images(full=True)

        for img_ref in image_list:
            xref = img_ref[0]
            try:
                base_image = doc.extract_image(xref)
                images.append({
                    'xref': xref,
                    'width': base_image['width'],
                    'height': base_image['height'],
                    'ext': base_image['ext'],
                    'image': base_image['image']
                })
            except Exception:
                continue

        return images

    def _save_image(self, doc, image_data: dict, output_dir: str,
                    spell_name: str, book_name: str, page_num: int) -> str | None:
        """Sla een afbeelding op als bestand."""
        # Maak veilige bestandsnaam
        safe_name = re.sub(r'[^a-z0-9_-]', '_', spell_name.lower())
        filename = f"{safe_name}.{image_data['ext']}"
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, 'wb') as f:
                f.write(image_data['image'])
            return filepath
        except Exception as e:
            print(f"  ✗ Kon afbeelding niet opslaan voor {spell_name}: {e}")
            return None

    def render_page_region(self, pdf_path: str, page_num: int,
                            rect: tuple, output_path: str, zoom: float = 2.0) -> str:
        """
        Render een specifiek rechthoekig gebied van een pagina als PNG.
        Handig voor het uitsnijden van een specifiek stuk tekst/afbeelding.
        rect = (x0, y0, x1, y1) in PDF-punten
        """
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        clip = fitz.Rect(rect)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        pix.save(output_path)
        doc.close()
        return output_path
