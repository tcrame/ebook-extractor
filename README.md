# 📚 eBook Extractor & Translator

Script Python pour extraire des chapitres depuis des fichiers EPUB ou des sites web, les traduire et générer de nouveaux EPUB ou PDF.

## ✨ Fonctionnalités

- 📖 **Extraction depuis EPUB** : Extrait et traduit des chapitres d'un fichier EPUB existant
- 🌐 **Téléchargement depuis le web** : Télécharge des chapitres depuis freewebnovel.com
- 🌍 **Traduction multilingue** : Support de Google Translate, DeepL et Microsoft Translator
- 📄 **Export multi-format** : Génère des fichiers EPUB ou PDF
- 🔄 **Système de retry intelligent** : Tentatives automatiques avec fallback
- 📁 **Gestion automatique des dossiers** : Crée les dossiers `input/` et `output/` automatiquement
- ⚙️ **Configuration flexible** : Tous les paramètres dans `config.json`

## 🚀 Installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances** (le script le fait automatiquement)
   ```bash
   python3 script.py
   ```

3. **Configurer les clés API** (optionnel, pour DeepL/Microsoft)
   ```bash
   cp config.json.example config.json
   # Éditez config.json avec vos clés
   ```

## 📖 Utilisation

### Mode EPUB local

1. **Placez vos fichiers EPUB** dans le dossier `input/` (créé automatiquement)

2. **Lancez le script**
   ```bash
   python3 script.py
   ```

3. **Suivez les instructions**
   - Choisissez l'option `2` (Fichier EPUB local)
   - Sélectionnez un fichier dans la liste
   - Choisissez une plage de chapitres (optionnel)
   - Sélectionnez le service de traduction
   - Choisissez le format de sortie (EPUB ou PDF)

4. **Récupérez votre fichier** dans le dossier `output/`

### Mode téléchargement web

1. **Lancez le script**
   ```bash
   python3 script.py
   ```

2. **Suivez les instructions**
   - Choisissez l'option `1` (Site web)
   - Entrez le nom du roman
   - Indiquez la plage de chapitres
   - Sélectionnez le service de traduction
   - Choisissez le format de sortie

3. **Récupérez votre fichier** dans le dossier `output/`

## ⚙️ Configuration

Le fichier `config.json` permet de configurer :

### Services de traduction

```json
"translation": {
  "deepl_api_key": "votre-clé-ici",
  "microsoft_api_key": "votre-clé-ici",
  "microsoft_region": "northeurope"
}
```

### Paramètres de retry

```json
"retry": {
  "max_attempts": 3,        // Nombre de tentatives
  "wait_multiplier": 2,     // Délai progressif (2s, 4s, 6s)
  "paragraph_delay": 0.3,   // Pause entre paragraphes
  "batch_delay": 0.5        // Pause entre lots de texte
}
```

### Dossiers

```json
"paths": {
  "input_folder": "input",    // Dossier des fichiers source
  "output_folder": "output"   // Dossier des fichiers générés
}
```

**Note :** Les dossiers sont créés automatiquement s'ils n'existent pas.

## 🌍 Services de traduction

### 1. Google Translate (par défaut)
- ✅ Gratuit et illimité
- ✅ Aucune clé API requise
- ⚠️ Qualité correcte

### 2. DeepL (recommandé)
- ✅ Meilleure qualité de traduction
- ✅ 500 000 caractères/mois gratuits
- 🔑 Nécessite une clé API : https://www.deepl.com/pro-api

### 3. Microsoft Translator
- ✅ Bonne qualité
- ✅ 2 000 000 caractères/mois gratuits
- 🔑 Nécessite une clé API Azure

## 📊 Structure des fichiers

```
ebook-extractor/
├── script.py              # Script principal
├── config.json            # Configuration (vos clés API)
├── config.json.example    # Modèle de configuration
├── README.md              # Ce fichier
├── README_CONFIG.md       # Documentation de la configuration
├── test_translation.py    # Script de test des traductions
├── input/                 # Dossier des fichiers EPUB source (créé auto)
│   └── votre-livre.epub
└── output/                # Dossier des fichiers générés (créé auto)
    └── votre-livre_1-50.pdf
```

## 🔄 Système de retry

Le script intègre un système intelligent de gestion des erreurs :

1. **3 tentatives** par défaut avec délais progressifs
2. **Fallback automatique** vers Google Translate en cas d'échec
3. **Conservation du texte original** si tout échoue
4. **Messages clairs** pour suivre le processus

## 🛠️ Dépannage

### Aucun fichier EPUB trouvé
```
❌ Aucun fichier EPUB trouvé dans le dossier 'input'
```
**Solution :** Placez vos fichiers `.epub` dans le dossier `input/`

### Erreur de clé API
```
⚠️ Clé API DeepL requise, utilisation de Google Translate
```
**Solution :** Vérifiez votre clé dans `config.json` ou utilisez Google Translate

### Erreur de traduction
```
⚠️ Tentative 1/3 échouée, nouvelle tentative dans 2s...
```
**Solution :** Le script réessaie automatiquement, patientez

## 📝 Exemples

### Traduire un livre complet
```bash
# 1. Placer le fichier dans input/
cp mon-livre.epub input/

# 2. Lancer le script
python3 script.py

# 3. Choisir :
#    - Option 2 (EPUB local)
#    - Sélectionner le fichier
#    - Tous les chapitres (appuyer Entrée)
#    - Service de traduction (1=Google, 2=DeepL, 3=Microsoft)
#    - Format de sortie (epub ou pdf)

# 4. Récupérer le fichier traduit dans output/
```

### Traduire une partie d'un livre
```bash
# Même procédure, mais :
# - Répondre "o" à "sélectionner une plage"
# - Indiquer le premier chapitre : 10
# - Indiquer le dernier chapitre : 20
# Résultat : mon-livre_10-20.pdf
```

## 🤝 Contribution

N'hésitez pas à contribuer en :
- Signalant des bugs
- Proposant des améliorations
- Ajoutant de nouvelles fonctionnalités

## 📄 Licence

Ce script est fourni tel quel pour un usage personnel.

## 🙏 Remerciements

- BeautifulSoup pour le parsing HTML
- ebooklib pour la manipulation d'EPUB
- deep-translator pour les services de traduction
- fpdf2 pour la génération de PDF

