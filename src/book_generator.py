"""
Module de génération de fichiers EPUB et PDF
"""
from ebooklib import epub
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from bs4 import BeautifulSoup


def create_epub(chapters, output_filename, metadata=None):
    """
    Crée un fichier EPUB à partir des chapitres

    Args:
        chapters (list): Liste de tuples (titre, contenu_html)
        output_filename (str): Nom du fichier EPUB de sortie
        metadata (dict): Dictionnaire contenant title, author, language
    """
    book = epub.EpubBook()

    # Métadonnées du livre (utiliser les métadonnées fournies ou valeurs par défaut)
    if metadata is None or not metadata:
        metadata = {
            'title': 'Unknown Book',
            'author': 'Unknown Author',
            'language': 'en'
        }

    # S'assurer que toutes les clés nécessaires existent
    metadata.setdefault('title', 'Unknown Book')
    metadata.setdefault('author', 'Unknown Author')
    metadata.setdefault('language', 'en')

    print(f"\n📚 Création de l'EPUB avec les métadonnées:")
    print(f"   Titre: {metadata['title']}")
    print(f"   Auteur: {metadata['author']}")
    print(f"   Langue: {metadata['language']}")

    _set_epub_metadata(book, metadata)

    # Créer les chapitres EPUB
    epub_chapters = _create_epub_chapters(book, chapters)

    # Configurer la structure du livre
    _configure_epub_structure(book, epub_chapters)

    # Écrire le fichier EPUB
    epub.write_epub(output_filename, book, {})
    print(f"\n✓ EPUB créé avec succès: {output_filename}")


def _set_epub_metadata(book, metadata):
    """Configure les métadonnées de l'EPUB"""
    book.set_identifier(f"{metadata.get('title', 'book').replace(' ', '-').lower()}-001")
    book.set_title(metadata.get('title', 'Unknown Title'))
    book.set_language(metadata.get('language', 'en'))
    book.add_author(metadata.get('author', 'Unknown Author'))


def _create_epub_chapters(book, chapters):
    """Crée les chapitres EPUB à partir du contenu"""
    epub_chapters = []

    for idx, (title, content) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=title,
            file_name=f'chapter_{idx}.xhtml',
            lang='en'
        )
        chapter.content = content
        book.add_item(chapter)
        epub_chapters.append(chapter)

    return epub_chapters


def _configure_epub_structure(book, epub_chapters):
    """Configure la table des matières et la structure du livre"""
    book.toc = tuple(epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + epub_chapters


def create_pdf(chapters, output_filename):
    """
    Crée un fichier PDF à partir des chapitres

    Args:
        chapters (list): Liste de tuples (titre, contenu_html)
        output_filename (str): Nom du fichier PDF de sortie
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Configuration des polices
    _setup_pdf_fonts(pdf)

    # Ajouter chaque chapitre
    for idx, (title, content_html) in enumerate(chapters, start=1):
        _add_chapter_to_pdf(pdf, title, content_html)

    pdf.output(output_filename)
    print(f"\n✓ PDF créé avec succès: {output_filename}")


def _setup_pdf_fonts(pdf):
    """Configure les polices pour le PDF"""
    pdf.add_font("DejaVu", style="", fname="DejaVuSans.ttf")
    pdf.add_font("DejaVu", style="B", fname="DejaVuSans-Bold.ttf")
    pdf.set_font("DejaVu", size=12)


def _add_chapter_to_pdf(pdf, title, content_html):
    """Ajoute un chapitre au PDF"""
    pdf.add_page()

    # Ajouter le titre
    pdf.set_font("DejaVu", style='B', size=12)
    pdf.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # Ajouter le contenu
    pdf.set_font("DejaVu", style='', size=10)
    soup = BeautifulSoup(content_html, 'html.parser')

    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text:
            try:
                pdf.multi_cell(0, 5, text)
                pdf.ln(1.5)
            except Exception as e:
                print(f"  ⚠️  Erreur lors de l'ajout d'un paragraphe: {e}")
                continue

