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

    Args:
        chapters (list): Liste de tuples (titre, contenu_html)
        service (str): Service de traduction
        api_key (str): Clé API
        region (str): Région Azure (pour Microsoft)
        retry_config (dict): Configuration des retry

    Returns:
        list: Liste de chapitres traduits
    """
    print("\n🔄 Traduction des chapitres en français...")
    translated_chapters = []
    paragraph_delay = retry_config.get('paragraph_delay', 0.3)

    # Barre de progression pour les chapitres
    for idx, (title, content) in enumerate(tqdm(chapters, desc="📚 Chapitres", unit="chapitre"), start=1):
        try:
            translated_chapter = _translate_single_chapter(
                title, content, service, api_key, region, retry_config, paragraph_delay, idx, len(chapters)
            )
            translated_chapters.append(translated_chapter)
        except Exception as e:
            tqdm.write(f"  ⚠️  Erreur chapitre {idx}: {e}, texte original conservé")
            translated_chapters.append((title, content))

    print(f"\n✓ {len(translated_chapters)} chapitre(s) traduit(s)")
    return translated_chapters


def _translate_single_chapter(title, content, service, api_key, region, retry_config, paragraph_delay, chapter_num, total_chapters):
    """Traduit un seul chapitre avec barre de progression des paragraphes"""
    # Traduire le titre
    translated_title = translate_text(
        title,
        service=service,
        api_key=api_key,
        region=region,
        retry_config=retry_config
    )

    # Traduire le contenu
    soup = BeautifulSoup(content, 'html.parser')
    translated_content = f"<h1>{translated_title}</h1>\n"

    paragraphs = soup.find_all('p')
    non_empty_paragraphs = [p for p in paragraphs if p.get_text(strip=True)]

    # Barre de progression pour les paragraphes du chapitre
    desc = f"  📄 Ch.{chapter_num}/{total_chapters}: {translated_title[:30]}..."
    for p in tqdm(non_empty_paragraphs, desc=desc, unit="§", leave=False):
        text = p.get_text(strip=True)
        translated_text = translate_text(
            text,
            service=service,
            api_key=api_key,
            region=region,
            retry_config=retry_config
        )
        translated_content += f"<p>{translated_text}</p>\n"
        time.sleep(paragraph_delay)

    return (translated_title, translated_content)

