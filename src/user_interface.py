"""
Module d'interface utilisateur pour la sélection des options
"""
import os
import sys


def display_welcome():
    """Affiche le message de bienvenue"""
    print("=== Téléchargement de chapitres et création d'EPUB ou PDF ===\n")


def display_config_info(config, input_folder, output_folder, retry_config):
    """Affiche les informations de configuration"""
    translation_config = config.get('translation', {})
    deepl_key = translation_config.get('deepl_api_key', '')
    microsoft_key = translation_config.get('microsoft_api_key', '')
    microsoft_region = translation_config.get('microsoft_region', 'northeurope')

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


def choose_source():
    """Demande à l'utilisateur de choisir la source des chapitres"""
    print("Source des chapitres:")
    print("  1. Site web (freewebnovel.com)")
    print("  2. Fichier EPUB local")
    return input("\nChoisissez une option (1/2) [1]: ") or "1"


def select_epub_file(epub_files, input_folder):
    """Permet à l'utilisateur de sélectionner un fichier EPUB"""
    print(f"\n📚 Fichiers EPUB disponibles dans '{input_folder}':")
    for idx, filename in enumerate(epub_files, start=1):
        file_path = os.path.join(input_folder, filename)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Taille en Mo
        print(f"  {idx}. {filename} ({file_size:.2f} Mo)")

    while True:
        choice = input(f"\nChoisissez un fichier (1-{len(epub_files)}): ").strip()
        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(epub_files):
                selected_file = epub_files[file_index]
                print(f"✓ Fichier sélectionné: {selected_file}")
                return selected_file
            else:
                print(f"⚠️  Veuillez choisir un nombre entre 1 et {len(epub_files)}")
        except ValueError:
            print("⚠️  Veuillez entrer un nombre valide")


def select_chapter_range(total_chapters):
    """Permet de sélectionner une plage de chapitres"""
    select_range = input("\nVoulez-vous sélectionner une plage de chapitres ? (o/n) [n]: ") or "n"

    if select_range.lower() == 'o':
        try:
            print(f"Chapitres disponibles: 1 à {total_chapters}")
            start = int(input("Premier chapitre à inclure: ") or "1")
            end = int(input("Dernier chapitre à inclure: ") or str(total_chapters))
            print(f"✓ Plage sélectionnée: chapitres {start} à {end}")
            return start, end
        except (ValueError, IndexError) as e:
            print(f"⚠️  Erreur de sélection, tous les chapitres seront utilisés: {e}")
            return 1, total_chapters

    return 1, total_chapters


def choose_translation_service(deepl_key, microsoft_key, microsoft_region, openai_key=None, openai_model=None, ollama_model=None, ollama_base_url=None):
    """Permet de choisir le service de traduction"""
    translate_choice = input("\nTraduire en français ? (o/n) [n]: ") or "n"

    if translate_choice.lower() != 'o':
        return False, 'google', None, None

    print("\nService de traduction:")
    print("  1. Google Translate (gratuit, illimité)")
    print("  2. DeepL (meilleure qualité, nécessite clé API)")
    print("  3. Microsoft Translator (nécessite clé API)")
    print("  4. OpenAI GPT (excellente qualité, nécessite clé API)")
    print("  5. Ollama (local, gratuit, nécessite Ollama installé)")
    service_choice = input("\nChoisissez un service (1/2/3/4/5) [1]: ") or "1"

    if service_choice == "2":
        return _configure_deepl(deepl_key)
    elif service_choice == "3":
        return _configure_microsoft(microsoft_key, microsoft_region)
    elif service_choice == "4":
        return _configure_openai(openai_key, openai_model)
    elif service_choice == "5":
        return _configure_ollama(ollama_model, ollama_base_url)
    else:
        return True, 'google', None, None


def _configure_deepl(deepl_key):
    """Configure le service DeepL"""
    if deepl_key:
        print("  → Utilisation de la clé DeepL depuis config.json")
        return True, 'deepl', deepl_key, None
    else:
        api_key = input("Clé API DeepL (ou Entrée pour Google): ").strip()
        if api_key:
            return True, 'deepl', api_key, None
        else:
            print("  → Aucune clé fournie, utilisation de Google Translate")
            return True, 'google', None, None


def _configure_microsoft(microsoft_key, microsoft_region):
    """Configure le service Microsoft"""
    if microsoft_key:
        print(f"  → Utilisation de la clé Microsoft depuis config.json (région: {microsoft_region})")
        return True, 'microsoft', microsoft_key, microsoft_region
    else:
        api_key = input("Clé API Microsoft (ou Entrée pour Google): ").strip() or None
        if api_key:
            region = input("Région Azure (ex: northeurope) [northeurope]: ").strip() or "northeurope"
            return True, 'microsoft', api_key, region
        return True, 'google', None, None


def _configure_openai(openai_key, openai_model):
    """Configure le service OpenAI"""
    if openai_key:
        print(f"  → Utilisation de la clé OpenAI depuis config.json (modèle: {openai_model})")
        return True, 'openai', openai_key, openai_model
    else:
        api_key = input("Clé API OpenAI (ou Entrée pour Google): ").strip() or None
        if api_key:
            model = input("Modèle (gpt-3.5-turbo/gpt-4) [gpt-3.5-turbo]: ").strip() or "gpt-3.5-turbo"
            return True, 'openai', api_key, model
        return True, 'google', None, None


def _configure_ollama(ollama_model, ollama_base_url):
    """Configure le service Ollama (local)"""
    print(f"  → Configuration Ollama")
    model = input(f"Modèle Ollama (ex: llama3, mistral) [{ollama_model}]: ").strip() or ollama_model
    base_url = input(f"URL Ollama [{ollama_base_url}]: ").strip() or ollama_base_url

    # Retourner un dict avec la config Ollama
    ollama_config = {
        'model': model,
        'base_url': base_url
    }
    return True, 'ollama', None, ollama_config


def choose_output_format_and_name(base_name, start_chapter, end_chapter, output_folder, default_format='pdf'):
    """Permet de choisir le format et le nom du fichier de sortie"""
    format_file = input(f"\nFormat de sortie (epub/pdf) [{default_format}]: ") or default_format

    default_output_name = f"{base_name}_{start_chapter}-{end_chapter}.{format_file}"
    output_name = input(f"Nom du fichier de sortie [{default_output_name}]: ") or default_output_name

    # Si l'utilisateur a juste donné un nom, l'ajouter au dossier de sortie
    if not os.path.dirname(output_name):
        output_file = os.path.join(output_folder, output_name)
    else:
        output_file = output_name

    return output_file, format_file


def get_web_download_info():
    """Récupère les informations pour le téléchargement web"""
    try:
        novel_name = input("Nom du roman (ex: the-primal-hunter): ") or "the-primal-hunter"
        base_url = f"https://freewebnovel.com/novel/{novel_name}"
        start_chapter = int(input("Numéro du premier chapitre (ex: 978): ") or "978")
        end_chapter = int(input("Numéro du dernier chapitre (ex: 980): ") or "980")
        return novel_name, base_url, start_chapter, end_chapter
    except ValueError:
        print("Erreur: Veuillez entrer des numéros valides")
        sys.exit(1)

