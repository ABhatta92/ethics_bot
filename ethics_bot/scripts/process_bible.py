import re
import polars as pl
from ethics_bot.utils.common import timeit
from ethics_bot.utils.constants import BIBLE_BOOK_MAPPING

# Regex patterns
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
