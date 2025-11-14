#!/usr/bin/env python3
"""
Script pour télécharger des chapitres depuis freewebnovel.com (ou autre URL de base) et les convertir en EPUB ou PDF
"""

import subprocess
import sys
import os
import warnings
import json

# Supprimer le warning urllib3/OpenSSL sur macOS
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')


def load_config():
    """
    Charge la configuration depuis le fichier config.json

    Returns:
        dict: Configuration avec les clés API, ou dict vide si fichier absent
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de config.json: {e}")
            return {}
    return {}


def setup_folders(config):
    """
    Crée les dossiers d'entrée et de sortie s'ils n'existent pas

    Args:
        config (dict): Configuration avec les chemins

    Returns:
        tuple: (input_folder, output_folder)
    """
    paths_config = config.get('paths', {})
    input_folder = paths_config.get('input_folder', 'input')
    output_folder = paths_config.get('output_folder', 'output')

    # Créer les dossiers s'ils n'existent pas
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"✓ Dossier d'entrée créé: {input_folder}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"✓ Dossier de sortie créé: {output_folder}")

    return input_folder, output_folder


def list_epub_files(folder):
    """
    Liste tous les fichiers EPUB dans un dossier

    Args:
        folder (str): Chemin du dossier

    Returns:
        list: Liste des fichiers EPUB
    """
    if not os.path.exists(folder):
        return []

    epub_files = [f for f in os.listdir(folder) if f.lower().endswith('.epub')]
    return sorted(epub_files)


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
        'deep_translator': 'deep-translator',
        'lxml': 'lxml'
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
from deep_translator import GoogleTranslator, DeeplTranslator, MicrosoftTranslator
import time


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
        metadata = {
            'title': book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else os.path.splitext(os.path.basename(epub_path))[0],
            'author': book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else 'Unknown',
            'language': book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else 'en'
        }

        print(f"📖 Lecture du fichier EPUB: {epub_path}")
        print(f"   Titre: {metadata['title']}")
        print(f"   Auteur: {metadata['author']}")

        # Récupérer tous les documents HTML de l'EPUB
        items = list(book.get_items_of_type(9))  # Type 9 = ITEM_DOCUMENT

        for idx, item in enumerate(items, start=1):
            try:
                content = item.get_content()
                soup = BeautifulSoup(content, 'xml')

                # Chercher le titre (h1, h2, ou title)
                title = None
                title_tag = soup.find(['h1', 'h2', 'h3'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                else:
                    # Utiliser le nom du fichier comme titre de secours
                    title = item.get_name() or f"Chapitre {idx}"

                # Extraire le contenu HTML
                body = soup.find('body')
                if body:
                    content_html = str(body)
                else:
                    content_html = str(soup)

                # Vérifier qu'il y a du contenu significatif
                text_content = soup.get_text(strip=True)

                # Filtrer les pages non-chapitres
                skip_keywords = [
                    'contents', 'table of contents', 'copyright', 'publisher',
                    'dedication', 'title page', 'cover', 'acknowledgments',
                    'about the author', 'also by', 'toc.xhtml', 'nav.xhtml'
                ]

                # Vérifier si c'est une page à sauter
                title_lower = title.lower()
                filename_lower = item.get_name().lower() if item.get_name() else ""

                should_skip = any(keyword in title_lower or keyword in filename_lower
                                 for keyword in skip_keywords)

                # Garder seulement si suffisamment de contenu et pas une page à sauter
                if len(text_content) > 200 and not should_skip:  # Au moins 200 caractères
                    chapters.append((title, content_html))
                    print(f"  ✓ Chapitre {len(chapters)} extrait: {title}")

            except Exception as e:
                print(f"  ⚠️  Erreur lors de l'extraction du chapitre {idx}: {e}")
                continue

        print(f"\n✓ {len(chapters)} chapitre(s) extrait(s) de l'EPUB")
        return chapters, metadata

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de l'EPUB: {e}")
        return [], {}


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


def translate_text(text, max_length=4500, service='google', api_key=None, region=None, retry_config=None):
    """
    Traduit un texte de l'anglais vers le français avec système de retry et fallback

    Args:
        text (str): Texte à traduire
        max_length (int): Longueur maximale par bloc
        service (str): Service de traduction ('google', 'deepl', 'microsoft')
        api_key (str): Clé API pour DeepL ou Microsoft (optionnelle pour Google)
        region (str): Région Azure pour Microsoft Translator (ex: 'northeurope')
        retry_config (dict): Configuration des tentatives (max_attempts, wait_multiplier, batch_delay)

    Returns:
        str: Texte traduit ou texte original si erreur
    """
    if not text or len(text.strip()) == 0:
        return text

    # Configuration par défaut si non fournie
    if retry_config is None:
        retry_config = {
            'max_attempts': 3,
            'wait_multiplier': 2,
            'batch_delay': 0.5
        }

    def try_translate(translator, text_to_translate, max_retries=None):
        """Tente de traduire avec retry"""
        if max_retries is None:
            max_retries = retry_config.get('max_attempts', 3)

        wait_multiplier = retry_config.get('wait_multiplier', 2)

        for attempt in range(max_retries):
            try:
                return translator.translate(text_to_translate)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * wait_multiplier  # Exemple: 2s, 4s, 6s avec multiplier=2
                    print(f"  ⚠️  Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative dans {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        return None

    def create_translator(svc, key, reg=None):
        """Crée un traducteur selon le service"""
        if svc == 'deepl':
            if not key:
                print("  ⚠️  Clé API DeepL requise, utilisation de Google Translate")
                return GoogleTranslator(source='en', target='fr'), 'google'
            return DeeplTranslator(api_key=key, source='en', target='fr'), 'deepl'
        elif svc == 'microsoft':
            if not key:
                print("  ⚠️  Clé API Microsoft requise, utilisation de Google Translate")
                return GoogleTranslator(source='en', target='fr'), 'google'
            return MicrosoftTranslator(api_key=key, source='en', target='fr', region=reg), 'microsoft'
        else:
            return GoogleTranslator(source='en', target='fr'), 'google'

    # Créer le traducteur principal
    translator, actual_service = create_translator(service, api_key, region)

    batch_delay = retry_config.get('batch_delay', 0.5)

    try:
        # Si le texte est trop long, le découper en morceaux
        if len(text) > max_length:
            sentences = text.split('. ')
            translated_parts = []
            current_batch = ""

            for sentence in sentences:
                if len(current_batch) + len(sentence) + 2 < max_length:
                    current_batch += sentence + ". "
                else:
                    if current_batch:
                        result = try_translate(translator, current_batch.strip())
                        if result:
                            translated_parts.append(result)
                        time.sleep(batch_delay)
                    current_batch = sentence + ". "

            if current_batch:
                result = try_translate(translator, current_batch.strip())
                if result:
                    translated_parts.append(result)

            return " ".join(translated_parts) if translated_parts else text
        else:
            return try_translate(translator, text)

    except Exception as e:
        # Fallback vers Google Translate si le service principal échoue
        if actual_service != 'google':
            print(f"  ⚠️  Erreur {actual_service}: {str(e)[:100]}")
            print(f"  🔄 Basculement vers Google Translate...")
            try:
                google_translator = GoogleTranslator(source='en', target='fr')

                if len(text) > max_length:
                    sentences = text.split('. ')
                    translated_parts = []
                    current_batch = ""

                    for sentence in sentences:
                        if len(current_batch) + len(sentence) + 2 < max_length:
                            current_batch += sentence + ". "
                        else:
                            if current_batch:
                                result = try_translate(google_translator, current_batch.strip())
                                if result:
                                    translated_parts.append(result)
                                time.sleep(batch_delay)
                            current_batch = sentence + ". "

                    if current_batch:
                        result = try_translate(google_translator, current_batch.strip())
                        if result:
                            translated_parts.append(result)

                    return " ".join(translated_parts) if translated_parts else text
                else:
                    return try_translate(google_translator, text)

            except Exception as google_error:
                print(f"  ❌ Google Translate a également échoué après 3 tentatives: {str(google_error)[:100]}")
                print(f"  → Texte original conservé")
                return text
        else:
            print(f"  ❌ Google Translate a échoué après 3 tentatives: {str(e)[:100]}")
            print(f"  → Texte original conservé")
            return text


def create_epub(chapters, output_filename="the_primal_hunter.epub", metadata=None):
    """
    Crée un fichier EPUB à partir des chapitres téléchargés

    Args:
        chapters (list): Liste de tuples (titre, contenu_html)
        output_filename (str): Nom du fichier EPUB de sortie
        metadata (dict): Dictionnaire contenant title, author, language
    """
    book = epub.EpubBook()

    # Métadonnées du livre (utiliser les métadonnées fournies ou valeurs par défaut)
    if metadata is None:
        metadata = {
            'title': 'The Primal Hunter',
            'author': 'Zogarth',
            'language': 'en'
        }

    book.set_identifier(f"{metadata.get('title', 'book').replace(' ', '-').lower()}-001")
    book.set_title(metadata.get('title', 'Unknown Title'))
    book.set_language(metadata.get('language', 'en'))
    book.add_author(metadata.get('author', 'Unknown Author'))

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

    # Charger la configuration
    config = load_config()
    translation_config = config.get('translation', {})
    deepl_key = translation_config.get('deepl_api_key', '')
    microsoft_key = translation_config.get('microsoft_api_key', '')
    microsoft_region = translation_config.get('microsoft_region', 'northeurope')

    # Configuration des retry
    retry_config = translation_config.get('retry', {
        'max_attempts': 3,
        'wait_multiplier': 2,
        'paragraph_delay': 0.3,
        'batch_delay': 0.5
    })

    # Configurer les dossiers
    input_folder, output_folder = setup_folders(config)

    if deepl_key or microsoft_key:
        print("✓ Configuration chargée depuis config.json")
        if deepl_key:
            print("  • Clé DeepL trouvée")
        if microsoft_key:
            print(f"  • Clé Microsoft trouvée (région: {microsoft_region})")
        print(f"  • Retry: {retry_config.get('max_attempts', 3)} tentatives, "
              f"délai x{retry_config.get('wait_multiplier', 2)}, "
              f"pause paragraphe: {retry_config.get('paragraph_delay', 0.3)}s")
        print(f"  • Dossier d'entrée: {input_folder}")
        print(f"  • Dossier de sortie: {output_folder}")
        print()

    # Demander la source des chapitres
    print("Source des chapitres:")
    print("  1. Site web (freewebnovel.com)")
    print("  2. Fichier EPUB local")
    source_choice = input("\nChoisissez une option (1/2) [1]: ") or "1"

    chapters = []
    translate_to_french = False
    metadata = None

    if source_choice == "2":
        # Mode EPUB local
        epub_files = list_epub_files(input_folder)

        if not epub_files:
            print(f"\n❌ Aucun fichier EPUB trouvé dans le dossier '{input_folder}'")
            print(f"   Veuillez placer vos fichiers EPUB dans ce dossier et relancer le script.")
            sys.exit(1)

        # Afficher la liste des fichiers EPUB disponibles
        print(f"\n📚 Fichiers EPUB disponibles dans '{input_folder}':")
        for idx, filename in enumerate(epub_files, start=1):
            file_path = os.path.join(input_folder, filename)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Taille en Mo
            print(f"  {idx}. {filename} ({file_size:.2f} Mo)")

        # Demander à l'utilisateur de choisir un fichier
        while True:
            choice = input(f"\nChoisissez un fichier (1-{len(epub_files)}): ").strip()
            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(epub_files):
                    selected_file = epub_files[file_index]
                    epub_path = os.path.join(input_folder, selected_file)
                    print(f"✓ Fichier sélectionné: {selected_file}")
                    break
                else:
                    print(f"⚠️  Veuillez choisir un nombre entre 1 et {len(epub_files)}")
            except ValueError:
                print("⚠️  Veuillez entrer un nombre valide")

        # Extraire les chapitres de l'EPUB
        print()
        chapters, metadata = extract_chapters_from_epub(epub_path)

        if not chapters:
            print("❌ Aucun chapitre n'a pu être extrait de l'EPUB")
            sys.exit(1)

        # Demander si l'utilisateur veut sélectionner une plage de chapitres
        start_chapter_num = 1
        end_chapter_num = len(chapters)
        select_range = input("\nVoulez-vous sélectionner une plage de chapitres ? (o/n) [n]: ") or "n"
        if select_range.lower() == 'o':
            try:
                print(f"Chapitres disponibles: 1 à {len(chapters)}")
                start_chapter_num = int(input("Premier chapitre à inclure: ") or "1")
                end_chapter_num = int(input("Dernier chapitre à inclure: ") or str(len(chapters)))
                start_idx = start_chapter_num - 1
                end_idx = end_chapter_num - 1
                chapters = chapters[start_idx:end_idx+1]
                print(f"✓ {len(chapters)} chapitre(s) sélectionné(s)")
            except (ValueError, IndexError) as e:
                print(f"⚠️  Erreur de sélection, tous les chapitres seront utilisés: {e}")
                start_chapter_num = 1
                end_chapter_num = len(chapters)

        # Demander si l'utilisateur veut traduire en français
        translate_choice = input("\nTraduire en français ? (o/n) [n]: ") or "n"
        translate_to_french = translate_choice.lower() == 'o'

        translation_service = 'google'
        translation_api_key = None
        translation_region = None

        if translate_to_french:
            print("\nService de traduction:")
            print("  1. Google Translate (gratuit, illimité)")
            print("  2. DeepL (meilleure qualité, nécessite clé API)")
            print("  3. Microsoft Translator (nécessite clé API)")
            service_choice = input("\nChoisissez un service (1/2/3) [1]: ") or "1"

            if service_choice == "2":
                translation_service = 'deepl'
                # Utiliser la clé du config.json si disponible, sinon demander
                if deepl_key:
                    translation_api_key = deepl_key
                    print("  → Utilisation de la clé DeepL depuis config.json")
                else:
                    translation_api_key = input("Clé API DeepL (ou Entrée pour Google): ").strip() or None
            elif service_choice == "3":
                translation_service = 'microsoft'
                # Utiliser la clé du config.json si disponible, sinon demander
                if microsoft_key:
                    translation_api_key = microsoft_key
                    translation_region = microsoft_region
                    print(f"  → Utilisation de la clé Microsoft depuis config.json (région: {microsoft_region})")
                else:
                    translation_api_key = input("Clé API Microsoft (ou Entrée pour Google): ").strip() or None
                    if translation_api_key:
                        translation_region = input("Région Azure (ex: northeurope) [northeurope]: ").strip() or "northeurope"

        # Format de sortie
        format_file = input("\nFormat de sortie (epub/pdf) [pdf]: ") or "pdf"

        # Extraire le nom de base du fichier EPUB
        epub_basename = os.path.splitext(os.path.basename(epub_path))[0]
        default_output_name = f"{epub_basename}_{start_chapter_num}-{end_chapter_num}.{format_file}"
        default_output = os.path.join(output_folder, default_output_name)

        output_name = input(f"Nom du fichier de sortie [{default_output_name}]: ") or default_output_name
        # Si l'utilisateur a juste donné un nom, l'ajouter au dossier de sortie
        if not os.path.dirname(output_name):
            output_file = os.path.join(output_folder, output_name)
        else:
            output_file = output_name

    else:
        # Mode téléchargement web (code original)
        try:
            novel_name = input("Nom du roman (ex: the-primal-hunter): ") or "the-primal-hunter"
            base_url = f"https://freewebnovel.com/novel/{novel_name}"
            start_chapter = int(input("Numéro du premier chapitre (ex: 978): ") or "978")
            end_chapter = int(input("Numéro du dernier chapitre (ex: 980): ") or "980")

            # Demander si l'utilisateur veut traduire en français
            translate_choice = input("Traduire en français ? (o/n) [n]: ") or "n"
            translate_to_french = translate_choice.lower() == 'o'

            translation_service = 'google'
            translation_api_key = None
            translation_region = None

            if translate_to_french:
                print("\nService de traduction:")
                print("  1. Google Translate (gratuit, illimité)")
                print("  2. DeepL (meilleure qualité, nécessite clé API)")
                print("  3. Microsoft Translator (nécessite clé API)")
                service_choice = input("\nChoisissez un service (1/2/3) [1]: ") or "1"

                if service_choice == "2":
                    translation_service = 'deepl'
                    # Utiliser la clé du config.json si disponible, sinon demander
                    if deepl_key:
                        translation_api_key = deepl_key
                        print("  → Utilisation de la clé DeepL depuis config.json")
                    else:
                        translation_api_key = input("Clé API DeepL (ou Entrée pour Google): ").strip() or None
                elif service_choice == "3":
                    translation_service = 'microsoft'
                    # Utiliser la clé du config.json si disponible, sinon demander
                    if microsoft_key:
                        translation_api_key = microsoft_key
                        translation_region = microsoft_region
                        print(f"  → Utilisation de la clé Microsoft depuis config.json (région: {microsoft_region})")
                    else:
                        translation_api_key = input("Clé API Microsoft (ou Entrée pour Google): ").strip() or None
                        if translation_api_key:
                            translation_region = input("Région Azure (ex: northeurope) [northeurope]: ").strip() or "northeurope"

            format_file = input("\nFormat de sortie (epub/pdf) [epub]: ") or "epub"
            default_output_name = f"{novel_name}_{start_chapter}-{end_chapter}.{format_file}"
            default_output = os.path.join(output_folder, default_output_name)

            output_name = input(f"Nom du fichier de sortie [{default_output_name}]: ") or default_output_name
            # Si l'utilisateur a juste donné un nom, l'ajouter au dossier de sortie
            if not os.path.dirname(output_name):
                output_file = os.path.join(output_folder, output_name)
            else:
                output_file = output_name
        except ValueError:
            print("Erreur: Veuillez entrer des numéros valides")
            sys.exit(1)

        print(f"\nTéléchargement des chapitres {start_chapter} à {end_chapter}...\n")

        # Télécharger chaque chapitre
        for chapter_num in range(start_chapter, end_chapter + 1):
            title, content = fetch_chapter(chapter_num, base_url)

            if title and content:
                chapters.append((title, content))
            else:
                # Demander si on continue en cas d'erreur
                response = input(f"\nChapitre {chapter_num} non disponible. Continuer? (o/n): ")
                if response.lower() != 'o':
                    break

            # Pause entre les requêtes pour ne pas surcharger le serveur
            time.sleep(1)

    # Vérifier le format de sortie
    if not output_file.endswith(('.epub', '.pdf')):
        output_file += f'.{format_file}'
    format_file = output_file.split('.')[-1].lower()
    if format_file not in ["epub", "pdf"]:
        print("Format non supporté. Utilisez 'epub' ou 'pdf'.")
        sys.exit(1)

    # Traduire les chapitres si demandé
    if translate_to_french and chapters:
        print("\n🔄 Traduction des chapitres en français...")
        translated_chapters = []

        for idx, (title, content) in enumerate(chapters, start=1):
            print(f"  🔄 Traduction du chapitre {idx}/{len(chapters)}: {title}")
            try:
                # Traduire le titre
                translated_title = translate_text(
                    title,
                    service=translation_service,
                    api_key=translation_api_key,
                    region=translation_region,
                    retry_config=retry_config
                )

                # Traduire le contenu
                soup = BeautifulSoup(content, 'html.parser')
                translated_content = f"<h1>{translated_title}</h1>\n"

                paragraphs = soup.find_all('p')
                paragraph_delay = retry_config.get('paragraph_delay', 0.3)

                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text:
                        translated_text = translate_text(
                            text,
                            service=translation_service,
                            api_key=translation_api_key,
                            region=translation_region,
                            retry_config=retry_config
                        )
                        translated_content += f"<p>{translated_text}</p>\n"
                        time.sleep(paragraph_delay)  # Pause entre chaque paragraphe (depuis config)

                translated_chapters.append((translated_title, translated_content))
                print(f"  ✓ Chapitre {idx} traduit: {translated_title}")
            except Exception as e:
                print(f"  ⚠️  Erreur lors de la traduction, chapitre ajouté dans la langue originale: {e}")
                translated_chapters.append((title, content))

        chapters = translated_chapters

    # Créer l'EPUB ou le PDF si au moins un chapitre a été téléchargé
    if chapters:
        print(f"\n{len(chapters)} chapitre(s) téléchargé(s)")
        if format_file == "epub":
            create_epub(chapters, output_file, metadata)
        else:
            create_pdf(chapters, output_file)
        print(f"\n✓ Processus terminé! {len(chapters)} chapitres dans {output_file}")
    else:
        print("\n✗ Aucun chapitre n'a été téléchargé")


if __name__ == "__main__":
    main()
