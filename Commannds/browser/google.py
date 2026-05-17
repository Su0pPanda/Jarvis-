from pathlib import Path
import tomllib
from urllib.parse import quote_plus
import webbrowser

CONFIG_PATH = Path(__file__).with_name("commands.toml")

with CONFIG_PATH.open("rb") as f:
    config = tomllib.load(f)
       
PHRASES = config["commands"][0]["phrases"]["ru"]
   
def handle_command(text: str) -> bool:
    text = text.lower()
    
    for phrase in PHRASES:
        if phrase in text:
            print("Команда найдена:", phrase)
            webbrowser.open("https://www.google.com/")
            return True

    return False


TYPE_GOOGLE_CONFIG_PATH = Path(__file__).with_name("typeGoogle.toml")

with TYPE_GOOGLE_CONFIG_PATH.open("rb") as f:
    typeConfig = tomllib.load(f)
       
TYPE_GOOGLE_PHRASES = sorted(
    typeConfig["commands"][0]["phrases"]["ru"],
    key=len,
    reverse=True,
)


def extract_query(text: str, phrases: list[str]) -> tuple[str | None, str]:
    for phrase in phrases:
        if phrase in text:
            query = text.replace(phrase, "", 1).strip(" ,.!?")
            return phrase, query
    return None, ""


def type_in_google(text: str) -> bool:
    text = text.lower().strip()
    phrase, query = extract_query(text, TYPE_GOOGLE_PHRASES)

    if not phrase:
        return False

    print("Команда найдена:", phrase)

    if not query:
        print("После команды нет текста для поиска.")
        return False

    try:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        webbrowser.open(search_url)
        return True
    except Exception as e:
        print(f"Error occurred while searching in Google: {e}")
        return False



if __name__ == "__main__":    
    type_in_google("за гугле в браузере погода в москве")
