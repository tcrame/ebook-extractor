import time
import logging
from typing import Optional
from deep_translator import GoogleTranslator, DeeplTranslator, MicrosoftTranslator

logger = logging.getLogger(__name__)

# Imports optionnels pour Gemini
try:
    from google import genai
    from google.genai.errors import APIError
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Imports optionnels pour OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Imports optionnels pour Ollama (via requests)
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


class GeminiTranslator:
    """Service de traduction s'appuyant sur l'API Google Gemini."""

    def __init__(
            self,
            api_key: str,
            model_name: str = "gemini-3.5-flash-lite",
            max_attempts: int = 3,
            wait_multiplier: float = 2.0,
    ):
        if not GEMINI_AVAILABLE:
            raise ImportError("Le package 'google-genai' n'est pas installé.")

        if not api_key:
            raise ValueError("Une clé d'API Gemini valide est requise.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.max_attempts = max_attempts
        self.wait_multiplier = wait_multiplier

    def translate_text(
            self,
            text: str,
            source_lang: str = "English",
            target_lang: str = "French",
            **kwargs,
    ) -> str:
        """Traduit un texte structuré en préservant le balisage HTML/XML."""
        if not text or not text.strip():
            return text

        prompt = (
            f"You are a professional literary translator. Translate the following text "
            f"from {source_lang} into {target_lang}.\n"
            f"CRITICAL REQUIREMENTS:\n"
            f"- Preserve all HTML/XML tags and attributes exactly as they appear in the source.\n"
            f"- Maintain line breaks and formatting structure.\n"
            f"- Do not add commentary, notes, or markdown code blocks (like ```html).\n\n"
            f"{text}"
        )

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                text_parts = []
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)

                result = "".join(text_parts).strip() if text_parts else (response.text.strip() if response.text else "")
                if result:
                    return result
                raise ValueError("La réponse de l'API Gemini est vide.")

            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str

                # Progression exponentielle : 5s, 10s, 20s, 40s, 80s...
                sleep_time = 5.0 * (self.wait_multiplier ** (attempt - 1))

                if is_rate_limit:
                    sleep_time = max(15.0, sleep_time)
                    _safe_print(f"  ⏳ Limite de requêtes Gemini atteinte (429/Quota). Pause de {sleep_time:.0f}s avant nouvelle tentative...")
                else:
                    _safe_print(f"  ⚠️  Tentative {attempt}/{self.max_attempts} échouée pour Gemini : {e}. Pause de {sleep_time:.0f}s...")

                if attempt == self.max_attempts:
                    raise e
                time.sleep(sleep_time)


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
            "options": {"temperature": 0.3}
        },
        timeout=120
    )
    response.raise_for_status()
    result = response.json()
    return result.get('response', '').strip()


def translate_text(
        text: str,
        source_lang: str = "en",
        target_lang: str = "fr",
        service: str = "google",
        config: Optional[dict] = None,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        retry_config: Optional[dict] = None,
        max_length: int = 4500,
        **kwargs,
) -> str:
    """
    Traduit un texte selon le service demandé (gemini, google, deepl, microsoft, openai, ollama)
    """
    if not text or len(text.strip()) == 0:
        return text

    if retry_config is None:
        retry_config = {
            'max_attempts': 3,
            'wait_multiplier': 2,
            'batch_delay': 0.5
        }

    # Cas Gemini
    if service == "gemini":
        gemini_key = None
        if config:
            gemini_key = config.get("translation", {}).get("gemini_api_key")
        final_key = gemini_key or api_key or kwargs.get("api_key")

        if not final_key:
            raise ValueError("Aucune clé d'API Gemini valide n'a été trouvée dans la configuration.")

        model_name = kwargs.get("model") or region or (config.get("translation", {}).get("gemini_model") if config else "gemini-3.5-flash-lite")
        max_attempts = retry_config.get("max_attempts", 3)
        wait_multiplier = retry_config.get("wait_multiplier", 2.0)

        translator = GeminiTranslator(
            api_key=final_key,
            model_name=model_name,
            max_attempts=max_attempts,
            wait_multiplier=wait_multiplier
        )
        return translator.translate_text(text, source_lang="English", target_lang="French")

    # Cas des autres traducteurs
    def try_translate(translator, text_to_translate, max_retries=None):
        if max_retries is None:
            max_retries = retry_config.get('max_attempts', 3)
        wait_multiplier = retry_config.get('wait_multiplier', 2.0)

        for attempt in range(1, max_retries + 1):
            try:
                return translator.translate(text_to_translate)
            except Exception as e:
                if attempt < max_retries:
                    # Progression exponentielle : 5s, 10s, 20s, 40s, 80s...
                    wait_time = 5.0 * (wait_multiplier ** (attempt - 1))
                    _safe_print(f"  ⚠️  Tentative {attempt}/{max_retries} échouée, nouvelle tentative dans {wait_time:.0f}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        return None

    def create_underlying_translator(svc, key, reg=None):
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

            class OpenAITranslator:
                def __init__(self, key_val, model_val='gpt-3.5-turbo'):
                    self.api_key = key_val
                    self.model = model_val if isinstance(model_val, str) else 'gpt-3.5-turbo'
                def translate(self, text_val):
                    return _translate_with_openai(text_val, self.api_key, self.model)

            model = reg if isinstance(reg, str) else 'gpt-3.5-turbo'
            return OpenAITranslator(key, model), 'openai'
        elif svc == 'ollama':
            class OllamaTranslator:
                def __init__(self, model_val='llama3', base_url_val='http://localhost:11434'):
                    self.model = model_val
                    self.base_url = base_url_val
                def translate(self, text_val):
                    return _translate_with_ollama(text_val, self.model, self.base_url)

            if isinstance(reg, dict):
                model = reg.get('model', 'llama3')
                base_url = reg.get('base_url', 'http://localhost:11434')
            else:
                model = 'llama3'
                base_url = 'http://localhost:11434'
            return OllamaTranslator(model, base_url), 'ollama'
        else:
            return GoogleTranslator(source='en', target='fr'), 'google'

    translator, actual_service = create_underlying_translator(service, api_key, region)
    batch_delay = retry_config.get('batch_delay', 0.5)

    try:
        if len(text) > max_length:
            return _translate_long_text(translator, text, max_length, batch_delay, try_translate)
        else:
            return try_translate(translator, text)
    except Exception as e:
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