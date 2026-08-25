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
    """Traduit un seul chapitre (d'un coup pour Gemini/LLM, ou paragraphe par paragraphe pour les APIs classiques)"""
    # Pour Gemini : traduire le chapitre entier d'un coup (1 seule requête incluant le titre)
    if service == "gemini":
        soup = BeautifulSoup(content, 'html.parser')
        body_tag = soup.find('body')
        raw_html = "".join(str(c) for c in (body_tag.contents if body_tag else soup.contents)).strip()

        # Si le contenu n'a pas déjà de balise de titre h1, on l'encapsule avec le titre
        if not raw_html.startswith("<h1"):
            full_html = f"<h1>{title}</h1>\n{raw_html}"
        else:
            full_html = raw_html

        translated_html = translate_text(
            full_html, service=service, api_key=api_key, region=region, retry_config=retry_config
        )

        # Extraire le titre traduit depuis le HTML traduit pour conserver la structure
        tsoup = BeautifulSoup(translated_html, 'html.parser')
        h1 = tsoup.find('h1')
        translated_title = h1.get_text(strip=True) if h1 else title

        # Pause de régulation de 4 secondes pour rester sous la limite des 15 RPM
        time.sleep(4)

        return (translated_title, translated_html)

    # Pour les services classiques (Google Translate, DeepL, etc.) : traduction par lots (batching)
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = soup.find_all('p')

    # 1. Traduction du titre
    translated_title = translate_text(
        title, service=service, api_key=api_key, region=region, retry_config=retry_config
    )

    translated_content = f"<h1>{translated_title}</h1>\n"

    # 2. Regroupement des paragraphes par lots (batching) pour réduire drastiquement les requêtes HTTP
    non_empty_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    desc = f"  📄 Ch.{chapter_num}/{total_chapters}: {translated_title[:25]}..."

    paragraph_delay = retry_config.get('paragraph_delay', 0.5) if retry_config else 0.5
    delimiter = "\n[[P_SEP]]\n"

    # Créer des lots de ~2 500 caractères max (bien sous la limite des 4 500)
    batches = []
    current_batch = []
    current_len = 0

    for text in non_empty_texts:
        added_len = len(text) + len(delimiter)
        if current_batch and (current_len + added_len > 2500):
            batches.append(current_batch)
            current_batch = [text]
            current_len = len(text)
        else:
            current_batch.append(text)
            current_len += added_len

    if current_batch:
        batches.append(current_batch)

    # Traduire lot par lot
    for batch in tqdm(batches, desc=desc, unit="lot", leave=False):
        joined_text = delimiter.join(batch)
        translated_batch_text = translate_text(
            joined_text,
            service=service,
            api_key=api_key,
            region=region,
            retry_config=retry_config
        )

        # Découper la réponse selon le délimiteur
        translated_paragraphs = translated_batch_text.split("[[P_SEP]]")

        # Sécurité si le délimiteur a été altéré : repli sur le nombre d'éléments
        if len(translated_paragraphs) == len(batch):
            for t_p in translated_paragraphs:
                translated_content += f"<p>{t_p.strip()}</p>\n"
        else:
            # Si le délimiteur a sauté, découper par lignes
            lines = [l.strip() for l in translated_batch_text.split("\n") if l.strip()]
            for line in lines:
                translated_content += f"<p>{line}</p>\n"

        time.sleep(paragraph_delay)

    return (translated_title, translated_content)