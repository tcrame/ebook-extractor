#!/usr/bin/env python3
"""
Script de test pour vérifier le système de traduction avec retry et fallback
"""

from script import translate_text, load_config

def test_translation():
    """Teste les différents services de traduction"""

    config = load_config()
    deepl_key = config.get('translation', {}).get('deepl_api_key', '')
    microsoft_key = config.get('translation', {}).get('microsoft_api_key', '')

    test_text = "Hello world, this is a test translation."

    print("=" * 60)
    print("TEST DES SERVICES DE TRADUCTION")
    print("=" * 60)

    # Test 1: Google Translate
    print("\n1️⃣  Test Google Translate (gratuit, sans clé)")
    print("-" * 60)
    result = translate_text(test_text, service='google')
    print(f"✅ Résultat: {result}\n")

    # Test 2: DeepL
    print("\n2️⃣  Test DeepL")
    print("-" * 60)
    if deepl_key:
        result = translate_text(test_text, service='deepl', api_key=deepl_key)
        print(f"✅ Résultat: {result}\n")
    else:
        print("⚠️  Pas de clé DeepL dans config.json\n")

    # Test 3: Microsoft
    print("\n3️⃣  Test Microsoft Translator")
    print("-" * 60)
    microsoft_region = config.get('translation', {}).get('microsoft_region', 'northeurope')
    if microsoft_key:
        print(f"Région: {microsoft_region}")
        result = translate_text(test_text, service='microsoft', api_key=microsoft_key, region=microsoft_region)
        print(f"✅ Résultat: {result}\n")
    else:
        print("⚠️  Pas de clé Microsoft dans config.json\n")

    # Test 4: Fallback avec clé invalide
    print("\n4️⃣  Test Fallback (clé invalide → Google)")
    print("-" * 60)
    result = translate_text(test_text, service='deepl', api_key='invalid-key-test')
    print(f"✅ Résultat: {result}\n")

    print("=" * 60)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("=" * 60)

if __name__ == "__main__":
    test_translation()

