"""
Module d'extraction de chapitres depuis des fichiers EPUB
"""
import os
from bs4 import BeautifulSoup
from ebooklib import epub


def extract_chapters_from_epub(epub_path):
    """
    Extrait tous les chapitres d'un fichier EPUB existant

    Args:
        epub_path (str): Chemin vers le fichier EPUB

    Returns:
        tuple: (chapters, metadata) où chapters est une liste de tuples (titre, contenu_html)
               et metadata est un dict avec title, author, language
    """
    try:
        book = epub.read_epub(epub_path)
        chapters = []

        # Extraire les métadonnées
        metadata = _extract_metadata(book, epub_path)

        print(f"📖 Lecture du fichier EPUB: {epub_path}")
        print(f"   Titre: {metadata['title']}")
        print(f"   Auteur: {metadata['author']}")

        # Récupérer tous les documents HTML de l'EPUB
        items = list(book.get_items_of_type(9))  # Type 9 = ITEM_DOCUMENT

        for idx, item in enumerate(items, start=1):
            chapter_info = _extract_chapter(item, idx)
            if chapter_info:
                chapters.append(chapter_info)
                print(f"  ✓ Chapitre {len(chapters)} extrait: {chapter_info[0]}")

        print(f"\n✓ {len(chapters)} chapitre(s) extrait(s) de l'EPUB")
        return chapters, metadata

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de l'EPUB: {e}")
        return [], {}


def _extract_metadata(book, epub_path):
    """Extrait les métadonnées du livre EPUB"""
    # Titre
    title_meta = book.get_metadata('DC', 'title')
    title = title_meta[0][0] if title_meta and title_meta[0] else os.path.splitext(os.path.basename(epub_path))[0]

    # Auteur : chercher creator ou contributor, avec gestion des formats chaîne ou tuple/dict
    author = 'Unknown Author'
    creator_meta = book.get_metadata('DC', 'creator') or book.get_metadata('DC', 'contributor')
    if creator_meta and creator_meta[0]:
        val = creator_meta[0][0]
        if isinstance(val, str) and val.strip():
            author = val.strip()
        elif isinstance(val, (tuple, list)) and len(val) > 0 and val[0]:
            author = str(val[0]).strip()

    # Langue
    lang_meta = book.get_metadata('DC', 'language')
    language = lang_meta[0][0] if lang_meta and lang_meta[0] else 'en'

    return {
        'title': title,
        'author': author,
        'language': language
    }


def _extract_chapter(item, idx):
    """Extrait un chapitre depuis un item EPUB"""
    try:
        content = item.get_content()
        soup = BeautifulSoup(content, 'xml')

        # Chercher le titre (h1, h2, ou title)
        title = _find_chapter_title(soup, item, idx)

        # Extraire le contenu HTML
        content_html = _extract_content_html(soup)

        # Vérifier qu'il y a du contenu significatif
        text_content = soup.get_text(strip=True)

        # Filtrer les pages non-chapitres
        if _should_skip_chapter(title, item.get_name(), text_content):
            return None

        return (title, content_html)

    except Exception as e:
        print(f"  ⚠️  Erreur lors de l'extraction du chapitre {idx}: {e}")
        return None


def _find_chapter_title(soup, item, idx):
    """Trouve le titre du chapitre"""
    title_tag = soup.find(['h1', 'h2', 'h3'])
    if title_tag:
        return title_tag.get_text(strip=True)
    else:
        return item.get_name() or f"Chapitre {idx}"


def _extract_content_html(soup):
    """Extrait le contenu HTML du chapitre"""
    body = soup.find('body')
    if body:
        return str(body)
    else:
        return str(soup)


def _should_skip_chapter(title, filename, text_content):
    """Détermine si un chapitre doit être ignoré"""
    skip_keywords = [
        'contents', 'table of contents', 'copyright', 'publisher',
        'dedication', 'title page', 'cover', 'acknowledgments',
        'about the author', 'also by', 'toc.xhtml', 'nav.xhtml'
    ]

    title_lower = title.lower()
    filename_lower = filename.lower() if filename else ""

    has_skip_keyword = any(keyword in title_lower or keyword in filename_lower
                          for keyword in skip_keywords)

    has_enough_content = len(text_content) > 200

    return has_skip_keyword or not has_enough_content

