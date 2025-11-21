# Configuration des clés API pour la traduction

## 📋 Format du fichier config.json

```json
{
  "translation": {
    "deepl_api_key": "votre-clé-deepl-ici",
    "microsoft_api_key": "votre-clé-microsoft-ici",
    "microsoft_region": "northeurope",
    "retry": {
      "max_attempts": 3,
      "wait_multiplier": 2,
      "paragraph_delay": 0.3,
      "batch_delay": 0.5
    }
  },
  "paths": {
    "input_folder": "input",
    "output_folder": "output"
  }
}
```

## 📁 Gestion des dossiers

Le script crée **automatiquement** les dossiers d'entrée et de sortie s'ils n'existent pas :

- **`input_folder`** : Dossier contenant vos fichiers EPUB à traiter
- **`output_folder`** : Dossier où seront générés les fichiers traduits

Vous pouvez personnaliser ces chemins dans `config.json`. Le script affichera :
```
✓ Dossier d'entrée créé: input
✓ Dossier de sortie créé: output
```

## 🔑 Obtenir les clés API

### DeepL
1. Créez un compte gratuit sur https://www.deepl.com/pro-api
2. Copiez votre clé API depuis le tableau de bord
3. Limite gratuite : 500 000 caractères/mois

### Microsoft Translator
1. Créez un compte Azure sur https://azure.microsoft.com/
2. Créez une ressource "Translator" dans le portail Azure
3. Copiez la clé depuis "Keys and Endpoint"
4. Notez votre région (ex: northeurope, westeurope, eastus)
5. Limite gratuite : 2 000 000 caractères/mois

### OpenAI (GPT)
1. Créez un compte sur https://platform.openai.com/
2. Ajoutez un moyen de paiement
3. Générez une clé API dans Settings > API Keys
4. Coût : ~0.002$/1000 tokens (GPT-3.5) ou ~0.03$/1000 tokens (GPT-4)

### Ollama (Local, gratuit)
1. Installez Ollama : https://ollama.com/download
2. Lancez : `ollama serve`
3. Téléchargez un modèle : `ollama pull llama3`
4. 100% gratuit, fonctionne hors ligne

## ⚙️ Configuration des paramètres de retry

### `max_attempts` (défaut: 3)
- Nombre maximum de tentatives en cas d'échec de traduction
- Valeur recommandée : 3-5

### `wait_multiplier` (défaut: 2)
- Multiplicateur pour le temps d'attente entre les tentatives
- Temps d'attente = (numéro_tentative × wait_multiplier) secondes
- Exemple avec multiplier=2 : 2s, 4s, 6s
- Valeur recommandée : 2-3

### `paragraph_delay` (défaut: 0.3)
- Délai en secondes entre la traduction de chaque paragraphe
- Permet d'éviter de surcharger l'API
- Valeur recommandée : 0.3-1.0

### `batch_delay` (défaut: 0.5)
- Délai en secondes entre les lots de texte long
- Utilisé quand un texte dépasse la limite de caractères
- Valeur recommandée : 0.5-2.0

## 💡 Exemples de configuration

### Configuration rapide (moins de pauses)
```json
"retry": {
  "max_attempts": 2,
  "wait_multiplier": 1,
  "paragraph_delay": 0.1,
  "batch_delay": 0.2
}
```

### Configuration stable (recommandée)
```json
"retry": {
  "max_attempts": 3,
  "wait_multiplier": 2,
  "paragraph_delay": 0.3,
  "batch_delay": 0.5
}
```

### Configuration prudente (connexion instable)
```json
"retry": {
  "max_attempts": 5,
  "wait_multiplier": 3,
  "paragraph_delay": 1.0,
  "batch_delay": 2.0
}
```

**Note :** Le fichier `config.json` est ignoré par git pour protéger vos clés API.

