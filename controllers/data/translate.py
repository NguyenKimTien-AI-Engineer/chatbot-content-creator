from configs import environment


async def translate_to_english(text):
    translator = environment.translator

    try:
        # Detect the language of the text (await the coroutine)
        detected = await translator.detect(text)

        # If the language is English, return the original text
        if detected.lang == 'en':
            return text

        # If not English, translate to English (await the coroutine)
        translated = await translator.translate(text, dest='en')
        print(f"Translated text: {translated.text}")
        return translated.text

    except Exception as e:
        # In case of errors (network, format, etc.), return the original text
        print(f"Error: {e}")
        return text
