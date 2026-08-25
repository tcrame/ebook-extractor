"""
Module de traduction de chapitres complets
"""
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from src.translator import translate_text


def translate_chapters(chapters, service, api_key, region, retry_config):
    """
    Traduit une liste de chapitres avec barre de progression
    """
    print("\n🔄 Traduction des chapitres en français...")
    translated_chapters = []

    for idx, (title, content) in enumerate(tqdm(chapters, desc="📚 Chapitres", unit="chapitre"), start=1):
        try:
            translated_chapter = _translate_single_chapter(
                title, content, service, api_key, region, retry_config, idx, len(chapters)
            )
            translated_chapters.append(translated_chapter)
        except Exception as e:
            tqdm.write(f"\n❌ Erreur lors de la traduction du chapitre {idx}: {e}")
            tqdm.write("  → Texte original conservé pour ce chapitre.\n")
            translated_chapters.append((title, content))

        # Pause sécurité entre deux chapitres
        time.sleep(1)

    print(f"\n✓ {len(translated_chapters)} chapitre(s) traité(s)")
    return translated_chapters


def _translate_single_chapter(title, content, service, api_key, region, retry_config, chapter_num, total_chapters):
    """Traduit un seul chapitre paragraphe par paragraphe avec pause anti-blocage"""
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = soup.find_all('p')

    # 1. Traduction du titre
    translated_title = translate_text(
        title, service=service, api_key=api_key, region=region, retry_config=retry_config
    )

    translated_content = f"<h1>{translated_title}</h1>\n"

    # 2. Traduction de chaque paragraphe
    desc = f"  📄 Ch.{chapter_num}/{total_chapters}: {translated_title[:25]}..."
    non_empty = [p for p in paragraphs if p.get_text(strip=True)]

    for p in tqdm(non_empty, desc=desc, unit="§", leave=False):
        text = p.get_text(strip=True)

        translated_text = translate_text(
            text,
            service=service,
            api_key=api_key,
            region=region,
            retry_config=retry_config
        )

        translated_content += f"<p>{translated_text}</p>\n"

        # Pause de 0.4s entre chaque paragraphe pour ne pas surcharger Google Translate
        time.sleep(0.4)

    return (translated_title, translated_content)