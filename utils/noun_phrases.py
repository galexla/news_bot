from textblob import TextBlob


def get_noun_phrases(text: str) -> list[str]:
    blob = TextBlob(text)
    return blob.noun_phrases
