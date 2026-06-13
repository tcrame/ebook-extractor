"""
Module de traduction avec support multi-services et retry
"""
import time
import json
from deep_translator import GoogleTranslator, DeeplTranslator, MicrosoftTranslator

# Imports optionnels pour les LLM
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


def _safe_print(message):
    """Affiche un message de manière compatible avec tqdm"""
    if TQDM_AVAILABLE:
        tqdm.write(message)
    else:
        print(message)


def _translate_with_openai(text, api_key, model='gpt-3.5-turbo'):
    """Traduit avec OpenAI GPT"""
    if not OPENAI_AVAILABLE:
        raise ImportError("Le package 'openai' n'est pas installé")

    openai.api_key = api_key

    prompt = f"Translate the following English text to French. Only provide the translation, nothing else:\n\n{text}"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional translator. Translate from English to French accurately and naturally."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def _translate_with_ollama(text, model='llama3', base_url='http://localhost:11434'):
    """Traduit avec Ollama (local)"""
    if not REQUESTS_AVAILABLE:
        raise ImportError("Le package 'requests' n'est pas installé")

    prompt = f"Translate the following English text to French. Only provide the translation, nothing else:\n\n{text}"

    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        },
        timeout=120
    )

    response.raise_for_status()
    result = response.json()
    return result.get('response', '').strip()


def translate_text(text, max_length=4500, service='google', api_key=None, region=None, retry_config=None):
    """
    Traduit un texte de l'anglais vers le français avec système de retry et fallback

    Args:
        text (str): Texte à traduire
        max_length (int): Longueur maximale par bloc
        service (str): Service de traduction ('google', 'deepl', 'microsoft', 'openai', 'ollama')
        api_key (str): Clé API (pour DeepL, Microsoft, OpenAI)
        region (str): Région Azure pour Microsoft Translator ou dict avec config LLM
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
                    wait_time = (attempt + 1) * wait_multiplier
                    _safe_print(f"  ⚠️  Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative dans {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        return None

    def create_translator(svc, key, reg=None):
        """Crée un traducteur selon le service"""
        if svc == 'deepl':
            if not key:
                _safe_print("  ⚠️  Clé API DeepL requise, utilisation de Google Translate")
                return GoogleTranslator(source='en', target='fr'), 'google'
            return DeeplTranslator(api_key=key, source='en', target='fr'), 'deepl'
        elif svc == 'microsoft':
            if not key:
                _safe_print("  ⚠️  Clé API Microsoft requise, utilisation de Google Translate")
                return GoogleTranslator(source='en', target='fr'), 'google'
            return MicrosoftTranslator(api_key=key, source='en', target='fr', region=reg), 'microsoft'
        elif svc == 'openai':
            if not key:
                _safe_print("  ⚠️  Clé API OpenAI requise, utilisation de Google Translate")
                return GoogleTranslator(source='en', target='fr'), 'google'
            # Pour OpenAI, on retourne un objet custom
            class OpenAITranslator:
                def __init__(self, api_key, model='gpt-3.5-turbo'):
                    self.api_key = api_key
                    self.model = model if isinstance(model, str) else 'gpt-3.5-turbo'
                def translate(self, text):
                    return _translate_with_openai(text, self.api_key, self.model)
            model = reg if isinstance(reg, str) else 'gpt-3.5-turbo'
            return OpenAITranslator(key, model), 'openai'
        elif svc == 'ollama':
            # Pour Ollama (local), pas besoin de clé API
            class OllamaTranslator:
                def __init__(self, model='llama3', base_url='http://localhost:11434'):
                    self.model = model
                    self.base_url = base_url
                def translate(self, text):
                    return _translate_with_ollama(text, self.model, self.base_url)

            # reg contient un dict avec model et base_url pour Ollama
            if isinstance(reg, dict):
                model = reg.get('model', 'llama3')
                base_url = reg.get('base_url', 'http://localhost:11434')
            else:
                model = 'llama3'
                base_url = 'http://localhost:11434'
            return OllamaTranslator(model, base_url), 'ollama'
        else:
            return GoogleTranslator(source='en', target='fr'), 'google'

    # Créer le traducteur principal
    translator, actual_service = create_translator(service, api_key, region)

    batch_delay = retry_config.get('batch_delay', 0.5)

    try:
        # Si le texte est trop long, le découper en morceaux
        if len(text) > max_length:
            return _translate_long_text(translator, text, max_length, batch_delay, try_translate)
        else:
            return try_translate(translator, text)

    except Exception as e:
        # Fallback vers Google Translate si le service principal échoue
        if actual_service != 'google':
            _safe_print(f"  ⚠️  Erreur {actual_service}: {str(e)[:100]}")
            _safe_print("  🔄 Basculement vers Google Translate...")
            return _fallback_to_google(text, max_length, batch_delay, try_translate)
        else:
            _safe_print(f"  ❌ Google Translate a échoué après 3 tentatives: {str(e)[:100]}")
            _safe_print("  → Texte original conservé")
            return text


def _translate_long_text(translator, text, max_length, batch_delay, try_translate):
    """Découpe et traduit un texte long en plusieurs parties"""
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


def _fallback_to_google(text, max_length, batch_delay, try_translate):
    """Bascule vers Google Translate en cas d'échec du service principal"""
    try:
        google_translator = GoogleTranslator(source='en', target='fr')

        if len(text) > max_length:
            return _translate_long_text(google_translator, text, max_length, batch_delay, try_translate)
        else:
            return try_translate(google_translator, text)

    except Exception as google_error:
        _safe_print(f"  ❌ Google Translate a également échoué après 3 tentatives: {str(google_error)[:100]}")
        _safe_print("  → Texte original conservé")
        return text

