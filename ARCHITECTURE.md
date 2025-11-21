# 📁 Structure du projet (Refactorisée)

Le code a été refactorisé en modules séparés pour améliorer la lisibilité et la maintenabilité.

## 🗂️ Architecture

```
ebook-extractor/
├── main.py                    # Point d'entrée principal
├── script.py                  # Ancien script monolithique (conservé)
├── src/                       # Package contenant tous les modules
│   ├── __init__.py            # Initialisation du package
│   ├── config_manager.py      # Gestion de la configuration et des dossiers
│   ├── user_interface.py      # Interface utilisateur (menus, sélections)
│   ├── epub_extractor.py      # Extraction de chapitres depuis EPUB
│   ├── web_downloader.py      # Téléchargement depuis le web
│   ├── translator.py          # Traduction multi-services avec retry
│   ├── chapter_translator.py  # Traduction de chapitres complets
│   └── book_generator.py      # Génération EPUB et PDF
├── config.json                # Configuration (clés API, paramètres)
├── input/                     # Dossier des fichiers EPUB source
└── output/                    # Dossier des fichiers générés
```

## 📦 Description des modules

### `main.py` - Script principal
- Point d'entrée de l'application
- Installe les dépendances automatiquement
- Orchestre le flux principal du programme

### `config_manager.py` - Gestion de la configuration
**Fonctions principales :**
- `load_config()` : Charge config.json
- `setup_folders()` : Crée les dossiers input/output
- `list_epub_files()` : Liste les fichiers EPUB disponibles

### `user_interface.py` - Interface utilisateur
**Fonctions principales :**
- `display_welcome()` : Message de bienvenue
- `choose_source()` : Choix entre web ou EPUB local
- `select_epub_file()` : Sélection d'un fichier EPUB
- `select_chapter_range()` : Sélection d'une plage de chapitres
- `choose_translation_service()` : Choix du service de traduction
- `choose_output_format_and_name()` : Choix du format et nom de sortie

### `epub_extractor.py` - Extraction depuis EPUB
**Fonctions principales :**
- `extract_chapters_from_epub()` : Extrait tous les chapitres
- `_extract_metadata()` : Extrait titre, auteur, langue
- `_extract_chapter()` : Extrait un chapitre individuel
- `_should_skip_chapter()` : Filtre les pages non-chapitres

### `web_downloader.py` - Téléchargement web
**Fonctions principales :**
- `download_chapters()` : Télécharge une série de chapitres
- `fetch_chapter()` : Télécharge un chapitre spécifique
- `_extract_title()` : Extrait le titre du chapitre
- `_extract_content()` : Extrait le contenu HTML

### `translator.py` - Traduction avec retry
**Fonctions principales :**
- `translate_text()` : Traduit un texte avec retry et fallback
- `_translate_long_text()` : Gère les textes longs
- `_fallback_to_google()` : Bascule vers Google en cas d'échec

**Services supportés :**
- Google Translate (gratuit, illimité)
- DeepL (500K caractères/mois gratuit)
- Microsoft Translator (2M caractères/mois gratuit)

### `chapter_translator.py` - Traduction de chapitres
**Fonctions principales :**
- `translate_chapters()` : Traduit une liste de chapitres
- `_translate_single_chapter()` : Traduit un chapitre complet

### `book_generator.py` - Génération EPUB/PDF
**Fonctions principales :**
- `create_epub()` : Génère un fichier EPUB
- `create_pdf()` : Génère un fichier PDF
- `_set_epub_metadata()` : Configure les métadonnées
- `_add_chapter_to_pdf()` : Ajoute un chapitre au PDF

## 🚀 Utilisation

### Avec le nouveau script modulaire
```bash
python3 main.py
```

### Avec l'ancien script (toujours disponible)
```bash
python3 script.py
```

Les deux scripts sont fonctionnels. Le nouveau (`main.py`) est plus lisible et maintenable.

## ✨ Avantages de la refactorisation

### 1. **Séparation des responsabilités**
Chaque module a une fonction claire et spécifique.

### 2. **Réutilisabilité**
Les modules peuvent être importés et utilisés dans d'autres projets.

### 3. **Testabilité**
Chaque module peut être testé indépendamment.

### 4. **Lisibilité**
Code plus court et plus facile à comprendre dans chaque fichier.

### 5. **Maintenabilité**
Modification d'une fonctionnalité sans toucher au reste.

## 🔧 Développement

### Ajouter un nouveau service de traduction
Modifier `translator.py` :
```python
def create_translator(svc, key, reg=None):
    if svc == 'nouveau_service':
        return NouveauTranslator(api_key=key), 'nouveau_service'
    # ...
```

### Ajouter un nouveau format de sortie
Modifier `book_generator.py` :
```python
def create_nouveau_format(chapters, output_filename):
    # Votre code ici
    pass
```

### Ajouter une nouvelle source de chapitres
Créer un nouveau module `nouvelle_source.py` et l'importer dans `main.py`.

## 📝 Convention de nommage

- **Fonctions publiques** : `function_name()`
- **Fonctions privées** : `_private_function()`
- **Modules** : `module_name.py` (snake_case)
- **Classes** : `ClassName` (PascalCase) - si ajoutées

## 🧪 Tests

Pour tester un module individuellement :
```python
# Tester la traduction
python3 -c "from src.translator import translate_text; print(translate_text('Hello world'))"

# Tester l'extraction EPUB
python3 -c "from src.epub_extractor import extract_chapters_from_epub; print(extract_chapters_from_epub('input/test.epub'))"
```

## 📚 Documentation

Chaque fonction est documentée avec :
- Description de ce qu'elle fait
- Args : Paramètres d'entrée
- Returns : Valeur de retour

Exemple :
```python
def translate_text(text, service='google'):
    """
    Traduit un texte de l'anglais vers le français
    
    Args:
        text (str): Texte à traduire
        service (str): Service de traduction
        
    Returns:
        str: Texte traduit
    """
```

## 🔄 Migration

Pour migrer de `script.py` vers `main.py` :

1. **Aucun changement nécessaire** - Les deux fonctionnent de la même manière
2. **Configuration identique** - Utilisent le même `config.json`
3. **Résultat identique** - Génèrent les mêmes fichiers

## 🎯 Prochaines améliorations possibles

- [ ] Ajouter des tests unitaires
- [ ] Ajouter un logger pour tracer les opérations
- [ ] Créer une interface graphique (GUI)
- [ ] Support de plus de langues cibles
- [ ] Support de plus de sources (autres sites web)
- [ ] Export en MOBI/AZW3 pour Kindle
- [ ] Traitement par lots (plusieurs fichiers)

