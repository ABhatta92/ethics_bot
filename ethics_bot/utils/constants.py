from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "ethics_bot"
DATA_ROOT = ROOT / "data"
LOGGER_PATH = ROOT / "logs"
RAW_PATH = DATA_ROOT / "raw"
INDEX_PATH = DATA_ROOT / "index"
METADATA_PATH = DATA_ROOT / "metadata"
EMBEDDED_PATH = DATA_ROOT / "embedded"
GUTENBERG_KJV_URL = "https://www.gutenberg.org/cache/epub/10/pg10.txt"
BIBLE_PATH = RAW_PATH / 'bible_kjv.txt'
TANZIL_PICKTHALL_URL = 'https://tanzil.net/trans/en.pickthall'
QURAN_PICKTHALL_PATH = RAW_PATH / 'en.pickthall.txt'
QURAN_SIMPLE_PATH = RAW_PATH / 'quran-simple-clean.txt'
TANAKH_URL = 'https://www.sefaria.org/api/texts/{}.{}?context=0&commentary=0&lang=en'
GITA_LINK = 'https://raw.githubusercontent.com/gita/gita/refs/heads/main/data/translation.json'
BIBLE_DATA = DATA_ROOT / 'bible'
QURAN_DATA = DATA_ROOT / 'quran'
GITA_DATA = DATA_ROOT / 'gita'


BIBLE_BOOK_MAPPING = {
    # --- Old Testament ---
    "The First Book of Moses: Called Genesis": "Genesis",
    "The Second Book of Moses: Called Exodus": "Exodus",
    "The Third Book of Moses: Called Leviticus": "Leviticus",
    "The Fourth Book of Moses: Called Numbers": "Numbers",
    "The Fifth Book of Moses: Called Deuteronomy": "Deuteronomy",
    "The Book of Joshua": "Joshua",
    "The Book of Judges": "Judges",
    "The Book of Ruth": "Ruth",
    "The First Book of Samuel": "1 Samuel",
    "The Second Book of Samuel": "2 Samuel",
    "The First Book of the Kings": "1 Kings",
    "The Second Book of the Kings": "2 Kings",
    "The First Book of the Chronicles": "1 Chronicles",
    "The Second Book of the Chronicles": "2 Chronicles",
    "Ezra": "Ezra",
    "The Book of Nehemiah": "Nehemiah",
    "The Book of Esther": "Esther",
    "The Book of Job": "Job",
    "The Book of Psalms": "Psalms",
    "The Proverbs": "Proverbs",
    "Ecclesiastes": "Ecclesiastes",
    "The Song of Solomon": "Song of Solomon",
    "The Book of the Prophet Isaiah": "Isaiah",
    "The Book of the Prophet Jeremiah": "Jeremiah",
    "The Lamentations of Jeremiah": "Lamentations",
    "The Book of the Prophet Ezekiel": "Ezekiel",
    "The Book of Daniel": "Daniel",
    "Hosea": "Hosea",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obadiah": "Obadiah",
    "Jonah": "Jonah",
    "Micah": "Micah",
    "Nahum": "Nahum",
    "Habakkuk": "Habakkuk",
    "Zephaniah": "Zephaniah",
    "Haggai": "Haggai",
    "Zechariah": "Zechariah",
    "Malachi": "Malachi",

    # --- New Testament ---
    "The Gospel According to Saint Matthew": "Matthew",
    "The Gospel According to Saint Mark": "Mark",
    "The Gospel According to Saint Luke": "Luke",
    "The Gospel According to Saint John": "John",
    "The Acts of the Apostles": "Acts",
    "The Epistle of Paul the Apostle to the Romans": "Romans",
    "The First Epistle of Paul the Apostle to the Corinthians": "1 Corinthians",
    "The Second Epistle of Paul the Apostle to the Corinthians": "2 Corinthians",
    "The Epistle of Paul the Apostle to the Galatians": "Galatians",
    "The Epistle of Paul the Apostle to the Ephesians": "Ephesians",
    "The Epistle of Paul the Apostle to the Philippians": "Philippians",
    "The Epistle of Paul the Apostle to the Colossians": "Colossians",
    "The First Epistle of Paul the Apostle to the Thessalonians": "1 Thessalonians",
    "The Second Epistle of Paul the Apostle to the Thessalonians": "2 Thessalonians",
    "The First Epistle of Paul the Apostle to Timothy": "1 Timothy",
    "The Second Epistle of Paul the Apostle to Timothy": "2 Timothy",
    "The Epistle of Paul the Apostle to Titus": "Titus",
    "The Epistle of Paul the Apostle to Philemon": "Philemon",
    "The Epistle of Paul the Apostle to the Hebrews": "Hebrews",
    "The General Epistle of James": "James",
    "The First Epistle General of Peter": "1 Peter",
    "The Second General Epistle of Peter": "2 Peter",
    "The First Epistle General of John": "1 John",
    "The Second Epistle General of John": "2 John",
    "The Third Epistle General of John": "3 John",
    "The General Epistle of Jude": "Jude",
    "The Revelation of Saint John the Divine": "Revelation",
}

TANAKH_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth",
    "I Samuel", "II Samuel",
    "I Kings", "II Kings",
    "I Chronicles", "II Chronicles",
    "Ezra", "Nehemiah", "Esther",
    "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Songs",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
    "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"
]

# if __name__ == "__main__":
#     for name, value in list(globals().items()):
#         if isinstance(value, Path):
#             print(f"{name}: {value}")
