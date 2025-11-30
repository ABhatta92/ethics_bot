import re, requests
import polars as pl
from ethics_bot.utils.common import *
from ethics_bot.utils.constants import *

RE_START = re.compile(r"\*\*\* START OF", re.IGNORECASE)
RE_END = re.compile(r"\*\*\* END OF", re.IGNORECASE)
RE_VERSE = re.compile(r"^(\d+):(\d+)\s+(.*)$")

@timeit
def process_bible(logger, path):
    in_text = False
    current_book = None
    current_chapter = None
    current_verse = None
    current_text = []
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            # --- Skip everything before "*** START" ---
            if not in_text:
                if RE_START.search(line):
                    in_text = True
                continue

            # --- Stop at "*** END" ---
            if RE_END.search(line):
                break

            # --- Check for a book header (exact match) ---
            if line in BIBLE_BOOK_MAPPING:
                # commit previous verse
                if current_book and current_verse and current_text:
                    records.append({
                        "book": current_book,
                        "chapter": int(current_chapter),
                        "verse": int(current_verse),
                        "text": " ".join(current_text).strip(),
                    })

                current_book = BIBLE_BOOK_MAPPING[line]
                current_chapter = None
                current_verse = None
                current_text = []
                continue

            # --- Check for verse pattern: "X:Y text" ---
            m = RE_VERSE.match(line)
            if m:
                chapter, verse, text = m.groups()

                # commit previous verse
                if current_book and current_verse is not None:
                    records.append({
                        "book": current_book,
                        "chapter": int(current_chapter),
                        "verse": int(current_verse),
                        "text": " ".join(current_text).strip(),
                    })

                current_chapter = chapter
                current_verse = verse
                current_text = [text.strip()]
                continue

            # --- Continuation line ---
            if line and current_text is not None:
                current_text.append(line)

    # --- Final commit ---
    if current_book and current_verse and current_text:
        records.append({
            "book": current_book,
            "chapter": int(current_chapter),
            "verse": int(current_verse),
            "text": " ".join(current_text).strip(),
        })

    df = pl.DataFrame(records)
    logger.info(f"Parsed {df.height} verses across {df['book'].n_unique()} books.")
    return df

def get_raw_bible(logger):
    resp = requests.get(GUTENBERG_KJV_URL)

    try:
        with open(BIBLE_PATH, 'w', encoding='utf-8') as file:
            file.write(resp.text)
            logger.info(f'Successfully written to {BIBLE_PATH}')
    except Exception as e:
        logger.error(f"Exception {e} while writing to {BIBLE_PATH}")


@timeit
def process_quran(logger, file_path, source="Pickthall"):
    records = []

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Skip blank lines or comments
            if not line or line.startswith("#"):
                continue

            parts = line.split("|", 2)
            if len(parts) != 3:
                logger.info(f"⚠️ Skipping malformed line: {line}")
                continue

            surah, ayah, text = parts
            records.append({
                "tradition": "Islam",
                "book": int(surah),
                "chapter": int(surah),
                "verse": int(ayah),
                "text": text.strip(),
                "lang": "EN",
                "source": source,
            })
    
    logger.info("Processed Quran Pickthall!")

    return pl.DataFrame(records)


@timeit
def process_gita(logger):
    resp = requests.get(GITA_LINK)
    logger.info(f'Status code: {resp.status_code}')

    df = pl.DataFrame(resp.json())

    df_filtered = df.filter(pl.col('language_id') == 1).filter(pl.col('author_id') == 19).sort("verse_id")
    author_name = df_filtered.select(pl.col('authorName').unique()).item()
    logger.info(f'Using author {author_name}')

    df_filtered = df_filtered.drop(['authorName', 'author_id', 'id', 'lang', 'language_id'])
    df_filtered = df_filtered.rename({'description':'text'})

    chapter_sizes = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78]

    chapter_numbers = []
    verse_numbers = []

    current = 0
    for chap_idx, size in enumerate(chapter_sizes, start=1):
        for verse_idx in range(1, size+1):
            chapter_numbers.append(chap_idx)
            verse_numbers.append(verse_idx)
            current += 1

    df_filtered = df_filtered.with_columns([
        pl.Series("chapter", chapter_numbers[:df_filtered.height]),
        pl.Series("verse", verse_numbers[:df_filtered.height])
    ])

    df_filtered = df_filtered.with_columns([
        pl.lit("Hinduism").alias("tradition"),
        pl.lit("Gita").alias("book"),
        pl.lit("EN").alias("lang"),
        pl.lit(author_name).alias("source")
    ])

    logger.info(f"Processed Gita rows: {df_filtered.height}")

    return df_filtered    