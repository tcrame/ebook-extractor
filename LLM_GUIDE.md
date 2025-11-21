# 🤖 Guide des services de traduction LLM

Le script supporte maintenant la traduction via des Large Language Models (LLM) pour une qualité supérieure !

## 📋 Services LLM disponibles

### 1. OpenAI (GPT-3.5 / GPT-4) ⭐⭐⭐⭐⭐

**Avantages :**
- Excellente qualité de traduction
- Très naturel et fluide
- Comprend le contexte
- Support de nombreuses langues

**Prix :**
- GPT-3.5-turbo : ~0.002$ / 1000 tokens (~750 mots)
- GPT-4 : ~0.03$ / 1000 tokens (~750 mots)

**Configuration :**
```json
{
  "translation": {
    "openai_api_key": "sk-votre-clé-ici",
    "openai_model": "gpt-3.5-turbo"
  }
}
```

**Obtenir une clé API :**
1. Créer un compte sur https://platform.openai.com/
2. Ajouter un moyen de paiement
3. Générer une clé API dans Settings > API Keys

---

### 2. Ollama (Local) ⭐⭐⭐⭐ 🆓

**Avantages :**
- 100% gratuit
- Fonctionne en local (confidentialité)
- Pas de limite de tokens
- Aucun coût

**Inconvénients :**
- Nécessite du matériel (GPU recommandé)
- Plus lent que les API cloud
- Qualité variable selon le modèle

**Modèles recommandés :**
- `llama3` (8B) - Bon compromis vitesse/qualité
- `llama3:70b` - Excellente qualité (nécessite beaucoup de RAM)
- `mistral` - Rapide et efficace
- `gemma2` - Bonne qualité

**Installation :**

1. **Installer Ollama :**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows
   # Télécharger depuis https://ollama.com/download
   ```

2. **Lancer le serveur Ollama :**
   ```bash
   ollama serve
   ```

3. **Télécharger un modèle :**
   ```bash
   # Modèle recommandé (4.7 GB)
   ollama pull llama3
   
   # Modèle plus puissant (40 GB)
   ollama pull llama3:70b
   
   # Modèle léger (4.1 GB)
   ollama pull mistral
   ```

**Configuration :**
```json
{
  "translation": {
    "ollama_model": "llama3",
    "ollama_base_url": "http://localhost:11434"
  }
}
```

---

## 📊 Comparaison des services

| Service | Qualité | Coût | Vitesse | Confidentialité |
|---------|---------|------|---------|-----------------|
| **OpenAI GPT-4** | ⭐⭐⭐⭐⭐ | $$$$ | ⚡⚡⚡ | ☁️ Cloud |
| **OpenAI GPT-3.5** | ⭐⭐⭐⭐ | $ | ⚡⚡⚡⚡ | ☁️ Cloud |
| **Ollama (llama3:70b)** | ⭐⭐⭐⭐⭐ | Gratuit | ⚡ | 🔒 Local |
| **Ollama (llama3)** | ⭐⭐⭐⭐ | Gratuit | ⚡⚡ | 🔒 Local |
| **DeepL** | ⭐⭐⭐⭐⭐ | $ | ⚡⚡⚡⚡ | ☁️ Cloud |
| **Google Translate** | ⭐⭐⭐ | Gratuit | ⚡⚡⚡⚡⚡ | ☁️ Cloud |

## 🚀 Utilisation

### Avec OpenAI

1. **Ajoutez votre clé dans config.json :**
   ```json
   {
     "translation": {
       "openai_api_key": "sk-proj-xxxxx",
       "openai_model": "gpt-3.5-turbo"
     }
   }
   ```

2. **Lancez le script :**
   ```bash
   python3 main.py
   ```

3. **Sélectionnez l'option 4 (OpenAI GPT)**

### Avec Ollama (Local)

1. **Assurez-vous qu'Ollama est lancé :**
   ```bash
   ollama serve
   ```

2. **Configurez dans config.json :**
   ```json
   {
     "translation": {
       "ollama_model": "llama3",
       "ollama_base_url": "http://localhost:11434"
     }
   }
   ```

3. **Lancez le script et sélectionnez l'option 5 (Ollama)**

## 💡 Conseils

### Pour OpenAI

- **GPT-3.5-turbo** : Bon rapport qualité/prix, suffisant pour la plupart des usages
- **GPT-4** : Meilleure qualité mais 15x plus cher, à utiliser pour du contenu critique
- Surveillez votre usage sur https://platform.openai.com/usage

### Pour Ollama

- **RAM nécessaire :**
  - llama3 (8B) : 8 GB RAM minimum
  - llama3:70b : 64 GB RAM minimum
  - mistral : 6 GB RAM minimum

- **GPU recommandé :**
  - Nvidia (CUDA) : Très rapide
  - Apple Silicon (M1/M2/M3) : Bon support
  - AMD (ROCm) : Support partiel

- **Premiers tests lents :**
  - Le premier appel charge le modèle en mémoire (30s-2min)
  - Les appels suivants sont beaucoup plus rapides

## 🔧 Dépannage

### OpenAI

**Erreur "Clé API invalide" :**
- Vérifiez que votre clé commence par `sk-`
- Vérifiez qu'elle est active sur platform.openai.com
- Assurez-vous d'avoir des crédits

**Erreur "Rate limit exceeded" :**
- Vous avez dépassé votre quota
- Attendez ou augmentez vos limites

### Ollama

**Erreur "Connection refused" :**
```bash
# Vérifier qu'Ollama est lancé
curl http://localhost:11434/api/version

# Relancer Ollama
ollama serve
```

**Modèle non trouvé :**
```bash
# Télécharger le modèle
ollama pull llama3

# Lister les modèles installés
ollama list
```

**Traduction lente :**
- Normal au premier appel (chargement du modèle)
- Vérifiez que vous avez assez de RAM
- Utilisez un modèle plus petit (mistral au lieu de llama3:70b)

## 💻 Utilisation d'Ollama en ligne de commande

Ollama offre une interface en ligne de commande très pratique pour tester et utiliser les modèles LLM.

### Commandes essentielles

#### 1. Lancer le serveur
```bash
# Démarrer Ollama en arrière-plan
ollama serve

# Vérifier que le serveur fonctionne
curl http://localhost:11434/api/version
```

#### 2. Gérer les modèles

**Télécharger un modèle :**
```bash
# Télécharger llama3 (4.7 GB)
ollama pull llama3

# Télécharger une version spécifique
ollama pull llama3:8b
ollama pull llama3:70b

# Autres modèles populaires
ollama pull mistral
ollama pull gemma2
ollama pull codellama
```

**Lister les modèles installés :**
```bash
ollama list

# Exemple de sortie :
# NAME              ID            SIZE    MODIFIED
# llama3:latest     a6990ed9be41  4.7 GB  2 hours ago
# mistral:latest    61e88e884507  4.1 GB  1 day ago
```

**Supprimer un modèle :**
```bash
ollama rm llama3
ollama rm mistral:latest
```

**Voir les informations d'un modèle :**
```bash
ollama show llama3

# Affiche : architecture, paramètres, taille, etc.
```

#### 3. Utiliser un modèle interactivement

**Mode chat :**
```bash
# Lancer une conversation avec llama3
ollama run llama3

# Vous pouvez alors poser des questions :
>>> Translate this to French: "Hello world"
Bonjour le monde

>>> exit  # Pour quitter
```

**Mode one-shot (une seule question) :**
```bash
# Poser une question directement
ollama run llama3 "Translate this to French: Hello world"

# Avec un prompt personnalisé
ollama run llama3 "You are a translator. Translate to French: The cat is on the table"
```

#### 4. Utiliser l'API REST

**Génération de texte :**
```bash
# Requête POST pour générer du texte
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Translate to French: Hello world",
  "stream": false
}'
```

**Mode chat :**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [
    {
      "role": "system",
      "content": "You are a professional translator."
    },
    {
      "role": "user",
      "content": "Translate to French: The weather is beautiful"
    }
  ],
  "stream": false
}'
```

### Exemples pratiques de traduction

#### Traduire un fichier texte
```bash
# Créer un script simple
cat > translate.sh << 'EOF'
#!/bin/bash
TEXT="$1"
ollama run llama3 "Translate this English text to French. Only provide the translation: $TEXT"
EOF

chmod +x translate.sh

# Utiliser le script
./translate.sh "The quick brown fox jumps over the lazy dog"
```

#### Traduire plusieurs lignes
```bash
# Utiliser un heredoc
ollama run llama3 << 'EOF'
Translate this English text to French. Only provide the translation:

The ancient dragon awakened from its millennia-long slumber.
His scales gleamed in the moonlight as he spread his massive wings.
The village below trembled in fear.
EOF
```

#### Traduction en lot (batch)
```bash
# Créer un fichier avec du texte à traduire
cat > to_translate.txt << 'EOF'
Hello world
Good morning
How are you?
EOF

# Traduire ligne par ligne
while IFS= read -r line; do
  echo "Original: $line"
  echo -n "French: "
  ollama run llama3 "Translate to French (only the translation): $line"
  echo "---"
done < to_translate.txt
```

### Paramètres avancés

**Contrôler la température (créativité) :**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Translate to French: beautiful day",
  "stream": false,
  "options": {
    "temperature": 0.3,
    "top_p": 0.9,
    "top_k": 40
  }
}'
```

**Paramètres disponibles :**
- `temperature` (0.0-2.0) : Créativité (0.3 recommandé pour traduction)
- `top_p` (0.0-1.0) : Diversité du vocabulaire
- `top_k` : Nombre de mots candidats
- `num_predict` : Longueur max de la réponse
- `seed` : Pour résultats reproductibles

### Script de traduction complet

Créer un script Python simple qui utilise Ollama :

```python
#!/usr/bin/env python3
import requests
import sys

def translate_with_ollama(text, model="llama3"):
    """Traduit un texte avec Ollama"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": f"Translate this English text to French. Only provide the translation:\n\n{text}",
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }
    )
    
    result = response.json()
    return result.get('response', '').strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./translate.py 'text to translate'")
        sys.exit(1)
    
    text = ' '.join(sys.argv[1:])
    translation = translate_with_ollama(text)
    print(translation)
```

**Utilisation :**
```bash
chmod +x translate.py
./translate.py "The hunter walked through the forest"
```

### Optimisation des performances

**Précharger un modèle en mémoire :**
```bash
# Le modèle reste en mémoire pour des réponses plus rapides
ollama run llama3 ""
# Ou
curl http://localhost:11434/api/generate -d '{"model":"llama3","keep_alive":-1}'
```

**Libérer la mémoire :**
```bash
# Décharger tous les modèles
curl http://localhost:11434/api/generate -d '{"model":"llama3","keep_alive":0}'
```

**Configurer le timeout :**
```bash
# Garder le modèle en mémoire pendant 1 heure
export OLLAMA_KEEP_ALIVE=3600
ollama serve
```

### Astuces pour de meilleures traductions

**1. Utiliser un prompt système clair :**
```bash
ollama run llama3 "You are a professional translator specializing in literature. Translate this English text to natural, fluent French: The dragon's roar echoed through the mountains."
```

**2. Traduire par paragraphes :**
```bash
# Meilleur contexte pour les longs textes
ollama run llama3 "Translate this paragraph to French, maintaining the narrative style:

The Hunter stood at the forest's edge. His journey had been long, but his determination unwavering. Beyond those ancient trees lay his destiny."
```

**3. Spécifier le registre de langue :**
```bash
ollama run llama3 "Translate to formal French for a novel: Good morning, Your Majesty"
ollama run llama3 "Translate to casual French: Hey dude, what's up?"
```

### Comparaison de modèles

**Tester plusieurs modèles :**
```bash
#!/bin/bash
TEXT="The ancient dragon awakened from its slumber."

for MODEL in llama3 mistral gemma2; do
    echo "=== $MODEL ==="
    ollama run $MODEL "Translate to French: $TEXT"
    echo ""
done
```

## 📦 Installation des dépendances

Le script installe automatiquement les dépendances, mais vous pouvez les installer manuellement :

```bash
# Pour OpenAI
pip install openai

# Pour Ollama (déjà inclus avec requests)
pip install requests
```

## 🎯 Recommandations

### Pour traduire un livre complet

**Meilleur rapport qualité/prix :**
- OpenAI GPT-3.5-turbo (~2-5$ pour un livre de 300 pages)

**Gratuit et illimité :**
- Ollama avec llama3 (si vous avez le matériel)

**Meilleure qualité absolue :**
- OpenAI GPT-4 (~30-50$ pour un livre de 300 pages)
- DeepL (500K caractères gratuits/mois)

### Pour quelques chapitres

**Tous les services conviennent**, privilégiez :
- DeepL (gratuit, excellente qualité)
- OpenAI GPT-3.5 (peu coûteux, très bon)
- Ollama (gratuit si déjà installé)

## 🌟 Exemple de qualité

### Texte original (anglais)
> "The Hunter stood at the edge of the forest, his heart pounding with anticipation. Beyond those ancient trees lay mysteries untold and dangers unimaginable."

### Google Translate
> "Le chasseur se tenait au bord de la forêt, le cœur battant d'anticipation. Au-delà de ces arbres anciens se trouvaient des mystères indicibles et des dangers inimaginables."

### DeepL
> "Le Chasseur se tenait à l'orée de la forêt, le cœur battant d'impatience. Au-delà de ces arbres anciens se cachaient des mystères indicibles et des dangers inimaginables."

### OpenAI GPT-4
> "Le Chasseur se tenait à la lisière de la forêt, le cœur battant d'anticipation. Au-delà de ces arbres séculaires se dissimulaient des mystères insondables et des dangers inimaginables."

### Ollama (llama3)
> "Le Chasseur se tenait en bordure de la forêt, le cœur palpitant d'impatience. Par-delà ces arbres ancestraux s'étendaient des mystères inexprimés et des périls inconcevables."

✨ Les LLM offrent souvent des traductions plus naturelles et contextuelles !

