#!/usr/bin/env python3
"""
Script pour télécharger des chapitres depuis freewebnovel.com (ou autre URL de base) et les convertir en EPUB ou PDF
"""

import subprocess
import sys
import os

# Fonction pour installer les dépendances manquantes
def install_dependencies():
    """
    Vérifie et installe les dépendances Python nécessaires
    """
    required_packages = {
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'ebooklib': 'ebooklib',
        'fpdf': 'fpdf2',
        'deep_translator': 'deep-translator'
    }

    missing_packages = []

    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"📦 Installation des dépendances manquantes: {', '.join(missing_packages)}")
        try:
            # Essayer d'abord avec --user (fonctionne mieux sur macOS/Linux)
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user', *missing_packages
            ])
            print("✅ Toutes les dépendances ont été installées avec succès!\n")
        except subprocess.CalledProcessError:
            # Si --user échoue (Windows ou environnement virtuel), réessayer sans
            try:
                print("⚠️  Tentative sans --user...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', *missing_packages
                ])
                print("✅ Toutes les dépendances ont été installées avec succès!\n")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de l'installation des dépendances: {e}")
                print("Veuillez installer manuellement avec: pip install requests beautifulsoup4 ebooklib fpdf2 deep-translator")
                sys.exit(1)

# Installer les dépendances si nécessaire
install_dependencies()

# Maintenant importer les modules
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from fpdf import FPDF
from deep_translator import GoogleTranslator
import time


def fetch_chapter(chapter_number, base_url):
    """
    Récupère le contenu d'un chapitre depuis l'URL

    Args:
        chapter_number (int): Numéro du chapitre
        base_url (str): URL de base du roman

    Returns:
        tuple: (titre, contenu_html) ou (None, None) si erreur
    """
    url = f"{base_url}/chapter-{chapter_number}"

    try:
        print(f"Téléchargement du chapitre {chapter_number}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouver le titre dans span.chapter
        title_span = soup.find('span', class_='chapter')
        if title_span:
            title = title_span.get_text(strip=True)
        else:
            title = f"Chapter {chapter_number}"

        # Trouver la div avec id="article"
        article_div = soup.find('div', id='article')
        if not article_div:
            print(f"  ⚠️  Div 'article' non trouvée pour le chapitre {chapter_number}")
            return None, None


        # Extraire tous les paragraphes
        paragraphs = article_div.find_all('p')
        if not paragraphs:
            print(f"  ⚠️  Aucun paragraphe trouvé pour le chapitre {chapter_number}")
            return None, None

        # Construire le contenu HTML
        content_html = f"<h1>{title}</h1>\n"
        for p in paragraphs:
            content_html += f"<p>{p.get_text(strip=True)}</p>\n"

        print(f"  ✓ Chapitre {chapter_number} téléchargé: {title}")
        return title, content_html

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Erreur lors du téléchargement du chapitre {chapter_number}: {e}")
        return None, None


def translate_text(text, max_length=4500):
    """
    Traduit un texte de l'anglais vers le français

    Args:
        text (str): Texte à traduire
        max_length (int): Longueur maximale par bloc

    Returns:
        str: Texte traduit ou texte original si erreur
    """
    if not text or len(text.strip()) == 0:
        return text

    try:
        translator = GoogleTranslator(source='en', target='fr')

        # Si le texte est trop long, le découper en morceaux
        if len(text) > max_length:
            # Découper par phrases pour éviter de couper au milieu d'une phrase
            sentences = text.split('. ')
            translated_parts = []
            current_batch = ""

            for sentence in sentences:
                if len(current_batch) + len(sentence) + 2 < max_length:
                    current_batch += sentence + ". "
                else:
                    if current_batch:
                        translated_parts.append(translator.translate(current_batch.strip()))
                        time.sleep(0.5)  # Pause pour éviter les limitations
                    current_batch = sentence + ". "

            if current_batch:
                translated_parts.append(translator.translate(current_batch.strip()))

            return " ".join(translated_parts)
        else:
            return translator.translate(text)
    except Exception as e:
        print(f"  ⚠️  Erreur de traduction: {e}, texte original conservé")
        return text


def create_epub(chapters, output_filename="the_primal_hunter.epub"):
    """
    Crée un fichier EPUB à partir des chapitres téléchargés

    Args:
        chapters (list): Liste de tuples (titre, contenu_html)
        output_filename (str): Nom du fichier EPUB de sortie
    """
    book = epub.EpubBook()

    # Métadonnées du livre
    book.set_identifier('primal-hunter-001')
    book.set_title('The Primal Hunter')
    book.set_language('en')
    book.add_author('Zogarth')

    # Liste des chapitres pour la table des matières
    epub_chapters = []
    spine = ['nav']

    # Créer un chapitre EPUB pour chaque chapitre téléchargé
    for idx, (title, content) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=title,
            file_name=f'chapter_{idx}.xhtml',
            lang='en'
        )
        chapter.content = content

        book.add_item(chapter)
        epub_chapters.append(chapter)
        spine.append(chapter)

    # Ajouter la table des matières
    book.toc = tuple(epub_chapters)

    # Ajouter les fichiers de navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Définir l'ordre de lecture
    book.spine = spine

    # Écrire le fichier EPUB
    epub.write_epub(output_filename, book, {})
    print(f"\n✓ EPUB créé avec succès: {output_filename}")


def create_pdf(chapters, output_filename="the_primal_hunter.pdf"):
    """
    Crée un fichier PDF à partir des chapitres téléchargés

    Args:
        chapters (list): Liste de tuples (titre, contenu_html)
        output_filename (str): Nom du fichier PDF de sortie
    """
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # fpdf2 inclut DejaVu nativement, pas besoin de fichiers externes
    pdf.add_font("DejaVu", style="", fname="DejaVuSans.ttf")
    pdf.add_font("DejaVu", style="B", fname="DejaVuSans-Bold.ttf")
    pdf.set_font("DejaVu", size=12)

    for idx, (title, content_html) in enumerate(chapters, start=1):
        pdf.add_page()
        pdf.set_font("DejaVu", style='B', size=12)  # Titre en 12pt (réduit de 16)
        # Utilisation de la nouvelle API fpdf2
        pdf.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)  # Espacement après le titre
        pdf.set_font("DejaVu", style='', size=10)  # Texte en 10pt (réduit de 12)
        soup = BeautifulSoup(content_html, 'html.parser')
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text:  # N'ajoute que les paragraphes non vides
                try:
                    pdf.multi_cell(0, 5, text)  # Hauteur de ligne réduite à 5
                    pdf.ln(1.5)  # Espacement entre les paragraphes réduit
                except Exception as e:
                    print(f"  ⚠️  Erreur lors de l'ajout d'un paragraphe: {e}")
                    continue

    pdf.output(output_filename)
    print(f"\n✓ PDF créé avec succès: {output_filename}")


def main():
    """
    Fonction principale
    """
    print("=== Téléchargement de chapitres et création d'EPUB ou PDF ===\n")

    # Demander les paramètres à l'utilisateur
    try:
        novel_name = input("Nom du roman (ex: the-primal-hunter): ") or "the-primal-hunter"
        base_url = f"https://freewebnovel.com/novel/{novel_name}"
        start_chapter = int(input("Numéro du premier chapitre (ex: 978): ") or "978")
        end_chapter = int(input("Numéro du dernier chapitre (ex: 980): ") or "980")

        # Demander si l'utilisateur veut traduire en français
        translate_choice = input("Traduire en français ? (o/n) [n]: ") or "n"
        translate_to_french = translate_choice.lower() == 'o'

        format_file = input("Format de sortie (epub/pdf) [epub]: ") or "epub"
        output_file = input(f"Nom du fichier de sortie (ex: {novel_name}.{format_file}): ") or f"{novel_name}.{format_file}"
        if not output_file.endswith(f'.{format_file}'):
            output_file += f'.{format_file}'
        format_file = format_file.lower()
        if format_file not in ["epub", "pdf"]:
            print("Format non supporté. Utilisez 'epub' ou 'pdf'.")
            sys.exit(1)
    except ValueError:
        print("Erreur: Veuillez entrer des numéros valides")
        sys.exit(1)

    print(f"\nTéléchargement des chapitres {start_chapter} à {end_chapter}...\n")

    chapters = []

    # Télécharger chaque chapitre
    for chapter_num in range(start_chapter, end_chapter + 1):
        title, content = fetch_chapter(chapter_num, base_url)

        if title and content:
            # Traduire si demandé
            if translate_to_french:
                print(f"  🔄 Traduction du chapitre {chapter_num} en français...")
                try:
                    # Traduire le titre
                    translated_title = translate_text(title)

                    # Traduire le contenu
                    soup = BeautifulSoup(content, 'html.parser')
                    translated_content = f"<h1>{translated_title}</h1>\n"

                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text:
                            translated_text = translate_text(text)
                            translated_content += f"<p>{translated_text}</p>\n"
                            time.sleep(0.3)  # Pause entre chaque paragraphe

                    chapters.append((translated_title, translated_content))
                    print(f"  ✓ Chapitre {chapter_num} traduit: {translated_title}")
                except Exception as e:
                    print(f"  ⚠️  Erreur lors de la traduction, chapitre ajouté en anglais: {e}")
                    chapters.append((title, content))
            else:
                chapters.append((title, content))
        else:
            # Demander si on continue en cas d'erreur
            response = input(f"\nChapitre {chapter_num} non disponible. Continuer? (o/n): ")
            if response.lower() != 'o':
                break

        # Pause entre les requêtes pour ne pas surcharger le serveur
        time.sleep(1)

    # Créer l'EPUB ou le PDF si au moins un chapitre a été téléchargé
    if chapters:
        print(f"\n{len(chapters)} chapitre(s) téléchargé(s)")
        if format_file == "epub":
            create_epub(chapters, output_file)
        else:
            create_pdf(chapters, output_file)
        print(f"\n✓ Processus terminé! {len(chapters)} chapitres dans {output_file}")
    else:
        print("\n✗ Aucun chapitre n'a été téléchargé")


if __name__ == "__main__":
    main()
