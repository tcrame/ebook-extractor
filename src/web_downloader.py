"""
Module de téléchargement de chapitres depuis le web
"""
import time
from bs4 import BeautifulSoup
from curl_cffi import requests


def fetch_chapter(chapter_number, base_url):
    """
    Récupère le contenu d'un chapitre depuis l'URL

    Args:
        chapter_number (int): Numéro du chapitre
        base_url (str): URL de base du roman

    Returns:
        tuple: (titre, contenu_html, auteur) ou (None, None, None) si erreur
    """
    url = f"{base_url}/chapter-{chapter_number}"

    try:
        print(f"Téléchargement du chapitre {chapter_number}...")

        # Empreinte Chrome pour contourner le blocage 403
        response = requests.get(url, impersonate="chrome", timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouver l'auteur dans les métadonnées
        author = _extract_author(soup)

        # Trouver le titre
        title = _extract_title(soup, chapter_number)

        # Trouver le contenu
        content_html = _extract_content(soup, chapter_number)

        if not content_html:
            return None, None, None

        print(f"  ✓ Chapitre {chapter_number} téléchargé: {title}")
        return title, content_html, author

    except Exception as e:
        print(f"  ✗ Erreur lors du téléchargement du chapitre {chapter_number}: {e}")
        return None, None, None


def _extract_author(soup):
    """Extrait l'auteur depuis les balises meta de la page"""
    # 1. <meta property="og:novel:author" content="...">
    meta = soup.find('meta', property='og:novel:author') or soup.find('meta', attrs={'name': 'og:novel:author'})
    if meta and meta.get('content'):
        return meta['content'].strip()

    # 2. <meta property="novel:author" content="..."> ou <meta name="author" content="...">
    meta_author = soup.find('meta', property='novel:author') or soup.find('meta', attrs={'name': 'author'})
    if meta_author and meta_author.get('content'):
        return meta_author['content'].strip()

    # 3. <meta property="og:book:author" content="...">
    meta_book_author = soup.find('meta', property='og:book:author')
    if meta_book_author and meta_book_author.get('content'):
        return meta_book_author['content'].strip()

    return None


def _extract_title(soup, chapter_number):
    """Extrait le titre du chapitre"""
    title_span = soup.find('span', class_='chapter')
    if title_span:
        return title_span.get_text(strip=True)
    else:
        return f"Chapter {chapter_number}"


def _extract_content(soup, chapter_number):
    """Extrait le contenu du chapitre"""
    article_div = soup.find('div', id='article')
    if not article_div:
        print(f"  ⚠️  Div 'article' non trouvée pour le chapitre {chapter_number}")
        return None

    # Extraire tous les paragraphes
    paragraphs = article_div.find_all('p')
    if not paragraphs:
        print(f"  ⚠️  Aucun paragraphe trouvé pour le chapitre {chapter_number}")
        return None

    # Construire le contenu HTML
    title = _extract_title(soup, chapter_number)
    content_html = f"<h1>{title}</h1>\n"
    for p in paragraphs:
        content_html += f"<p>{p.get_text(strip=True)}</p>\n"

    return content_html


def download_chapters(start_chapter, end_chapter, base_url):
    """
    Télécharge une série de chapitres depuis le web

    Args:
        start_chapter (int): Numéro du premier chapitre
        end_chapter (int): Numéro du dernier chapitre
        base_url (str): URL de base du roman

    Returns:
        tuple: (chapters, detected_author) où chapters est une liste de tuples (titre, contenu_html)
    """
    chapters = []
    detected_author = None

    print(f"\nTéléchargement des chapitres {start_chapter} à {end_chapter}...\n")

    for chapter_num in range(start_chapter, end_chapter + 1):
        title, content, author = fetch_chapter(chapter_num, base_url)

        if author and not detected_author:
            detected_author = author

        if title and content:
            chapters.append((title, content))
        else:
            # Demander si on continue en cas d'erreur
            resp = input(f"\nChapitre {chapter_num} non disponible. Continuer? (o/n): ")
            if resp.lower() != 'o':
                break

        # Pause de 2 secondes pour éviter d'être banni par le serveur
        time.sleep(2)

    return chapters, detected_author