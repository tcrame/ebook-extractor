"""
Module de traduction avec support multi-services et retry
"""
import time
from googletrans import Translator as GoogleTranslator

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


def translate_text(text, max_length=4500, service='google', api_key=None, region=None, retry_config=None):
    """
    Traduit un texte de l'anglais vers le français avec système de retry
    """
    if not text or len(text.strip()) == 0:
        return text

    if retry_config is None:
        retry_config = {
            'max_attempts': 3,
            'wait_multiplier': 2,
            'batch_delay': 0.5
        }

    max_retries = retry_config.get('max_attempts', 3)
    wait_multiplier = retry_config.get('wait_multiplier', 2)

    # Initialisation de Google Translator
    translator = GoogleTranslator()

    for attempt in range(max_retries):
        try:
            # googletrans 4.0.0-rc1 renvoie un objet avec .text
            result = translator.translate(text, src='en', dest='fr')
            return result.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * wait_multiplier
                _safe_print(f"  ⚠️  Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative dans {wait_time}s...")
                time.sleep(wait_time)
            else:
                _safe_print(f"  ❌ Google Translate a échoué après {max_retries} tentatives: {str(e)[:100]}")
                _safe_print("  → Texte original conservé")
                return text

    return text