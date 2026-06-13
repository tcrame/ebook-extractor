"""
Module de gestion de la configuration
"""
import os
import json


def load_config():
    """
    Charge la configuration depuis le fichier config.json

    Returns:
        dict: Configuration avec les clés API, ou dict vide si fichier absent
    """
    # Remonter au dossier parent (racine du projet) depuis le dossier src
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

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

