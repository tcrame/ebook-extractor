#!/usr/bin/env python3
"""
Script principal pour extraire des chapitres depuis EPUB ou web et les traduire
"""

import subprocess
import sys
import os
import warnings

# Supprimer le warning urllib3/OpenSSL sur macOS
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')


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
        'lxml': 'lxml',
        'tqdm': 'tqdm'
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
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user', *missing_packages
            ])
            print("✅ Toutes les dépendances ont été installées avec succès!\n")
        except subprocess.CalledProcessError:
            try:
                print("⚠️  Tentative sans --user...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', *missing_packages
                ])
                print("✅ Toutes les dépendances ont été installées avec succès!\n")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de l'installation des dépendances: {e}")
                print("Veuillez installer manuellement avec: pip install requests beautifulsoup4 ebooklib fpdf2 deep-translator lxml")
                sys.exit(1)


# Installer les dépendances si nécessaire
install_dependencies()

# Importer les modules personnalisés depuis le package src
from src.config_manager import load_config, setup_folders, list_epub_files
from src.user_interface import (
    display_welcome, display_config_info, choose_source,
    select_epub_file, select_chapter_range, choose_translation_service,
    choose_output_format_and_name, get_web_download_info
)
from src.epub_extractor import extract_chapters_from_epub
from src.web_downloader import download_chapters
from src.chapter_translator import translate_chapters
from src.book_generator import create_epub, create_pdf


def configure_translation(config):
    """Configure uniquement le service de traduction (avant téléchargement)"""
    translation_config = config.get('translation', {})

    translate_to_french, service, api_key, region = choose_translation_service(
        translation_config.get('deepl_api_key', ''),
        translation_config.get('microsoft_api_key', ''),
        translation_config.get('microsoft_region', 'northeurope'),
        translation_config.get('openai_api_key', ''),
        translation_config.get('openai_model', 'gpt-3.5-turbo'),
        translation_config.get('ollama_model', 'llama3'),
        translation_config.get('ollama_base_url', 'http://localhost:11434')
    )

    return translate_to_french, service, api_key, region


def process_epub_source(input_folder, output_folder, translate_to_french, service, api_key, region):
    """Traite une source EPUB locale"""
    epub_files = list_epub_files(input_folder)

    if not epub_files:
        print(f"\n❌ Aucun fichier EPUB trouvé dans le dossier '{input_folder}'")
        print("   Veuillez placer vos fichiers EPUB dans ce dossier et relancer le script.")
        sys.exit(1)

    # Sélection du fichier
    selected_file = select_epub_file(epub_files, input_folder)
    epub_path = os.path.join(input_folder, selected_file)

    # Extraction des chapitres
    print()
    chapters, metadata = extract_chapters_from_epub(epub_path)

    if not chapters:
        print("❌ Aucun chapitre n'a pu être extrait de l'EPUB")
        sys.exit(1)

    # Sélection de la plage de chapitres
    start_chapter_num, end_chapter_num = select_chapter_range(len(chapters))
    if start_chapter_num != 1 or end_chapter_num != len(chapters):
        start_idx = start_chapter_num - 1
        end_idx = end_chapter_num - 1
        chapters = chapters[start_idx:end_idx + 1]
        print(f"✓ {len(chapters)} chapitre(s) sélectionné(s)")

    # Configuration du format de sortie
    epub_basename = os.path.splitext(os.path.basename(epub_path))[0]
    output_file, format_file = choose_output_format_and_name(
        epub_basename, start_chapter_num, end_chapter_num, output_folder, 'pdf'
    )

    return chapters, metadata, output_file, format_file


def process_web_source(output_folder, translate_to_french, service, api_key, region):
    """Traite une source web"""
    # Récupérer les informations de téléchargement
    novel_name, base_url, start_chapter, end_chapter = get_web_download_info()

    # Configuration du format de sortie AVANT téléchargement
    output_file, format_file = choose_output_format_and_name(
        novel_name, start_chapter, end_chapter, output_folder, 'epub'
    )

    # Télécharger les chapitres
    chapters = download_chapters(start_chapter, end_chapter, base_url)

    # Créer les métadonnées basées sur le nom du roman
    title = ' '.join(word.capitalize() for word in novel_name.replace('-', ' ').replace('_', ' ').split())
    metadata = {
        'title': title,
        'author': 'Unknown Author',
        'language': 'en'
    }

    return chapters, metadata, output_file, format_file


def main():
    """
    Fonction principale
    """
    display_welcome()

    # Charger la configuration
    config = load_config()
    translation_config = config.get('translation', {})

    # Configuration des retry
    retry_config = translation_config.get('retry', {
        'max_attempts': 3,
        'wait_multiplier': 2,
        'paragraph_delay': 0.3,
        'batch_delay': 0.5
    })

    # Configurer les dossiers
    input_folder, output_folder = setup_folders(config)

    # Afficher les informations de configuration
    display_config_info(config, input_folder, output_folder, retry_config)

    # Choisir la source
    source_choice = choose_source()

    # Configuration de la traduction (AVANT téléchargement)
    translate_to_french, service, api_key, region = configure_translation(config)

    # Traiter selon la source choisie
    if source_choice == "2":
        chapters, metadata, output_file, format_file = \
            process_epub_source(input_folder, output_folder, translate_to_french, service, api_key, region)
    else:
        chapters, metadata, output_file, format_file = \
            process_web_source(output_folder, translate_to_french, service, api_key, region)

    # Vérifier le format de sortie
    if not output_file.endswith(('.epub', '.pdf')):
        output_file += f'.{format_file}'
    format_file = output_file.split('.')[-1].lower()
    if format_file not in ["epub", "pdf"]:
        print("Format non supporté. Utilisez 'epub' ou 'pdf'.")
        sys.exit(1)

    # Traduire les chapitres si demandé
    if translate_to_french and chapters:
        chapters = translate_chapters(chapters, service, api_key, region, retry_config)

    # Créer l'EPUB ou le PDF
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

