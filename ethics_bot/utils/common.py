import logging, requests, time, os
from functools import wraps
import numpy as np
import polars as pl
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style
import xml.etree.ElementTree as ET 
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ethics_bot.utils.constants import *

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        level_name = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        log_fmt = f"%(asctime)s | %(name)s | {level_name} | %(message)s"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
    
def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = kwargs.get("logger", None)

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start

        # If logger provided → log
        if logger:
            logger.info(f"{func.__name__} completed in {duration:.4f} sec")
        else:
            print(f"{func.__name__} completed in {duration:.4f} sec")

        return result
    return wrapper

def get_logger(name: str, log_file, maxBytes=5_000_000, backupCount=5, level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.hasHandlers():  # prevent duplicate handlers
        return logger

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())

    # Rotating file handler (5 MB per file, 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=maxBytes, backupCount=backupCount)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    ))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def print_dict(d):
    for k,v in d.items():
        print(f"{k}:{v}")

@timeit
def embed_text(logger, df, book, batch_size):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    texts = df["clean_text"].to_list()
    logger.info("Generating bible verse embeddings")
    start = time.time()
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    end = time.time()
    embeddings = np.array(embeddings, dtype="float32")
    logger.info(f"Time taken for embeddings = {end-start:.2f} ")
    logger.info(f"Throughput: {len(texts) / (end - start):.2f} verses/sec")

    logger.info(f"Saving embeddings to {book}_embeddings.npy")
    np.save(os.path.join(os.path.join(DATA_ROOT, book), f"{book}_embeddings.npy"), embeddings)
    logger.info(f"Writing metadata to {book}_metadata.parquet")
    df.write_parquet(os.path.join(os.path.join(DATA_ROOT, book), f"{book}_metadata.parquet"))

@timeit
def clean_text(logger, df):
    df = df.with_columns(
    pl.col("text")
      # 1. Remove bracketed content
      .str.replace_all(r"\[[^\]]+\]", "")
      # 2. Remove non-ASCII chars
      .str.replace_all(r"[^\x00-\x7F]+", " ")
      # 3. Collapse multiple spaces/newlines
      .str.replace_all(r"\s+", " ")
      # 4. Trim edges
      .str.strip_chars()
      .alias("clean_text")
    )
    return df

analyzer = SentimentIntensityAnalyzer()

def get_sentiment_row(text):
    if not text or not isinstance(text, str):
        return (0.0, 0.0, 0.0, 0.0)
    s = analyzer.polarity_scores(text)
    return (s["neg"], s["neu"], s["pos"], s["compound"])

@timeit
def add_sentiments(logger, df):
    logger.info("Adding sentiments to cleansed text")
    sent_list = [get_sentiment_row(t) for t in df["clean_text"].to_list()]
    neg, neu, pos, comp = zip(*sent_list)

    df = df.with_columns([
        pl.Series("sent_neg",  neg),
        pl.Series("sent_neu",  neu),
        pl.Series("sent_pos",  pos),
        pl.Series("sent_comp", comp)
    ])

    return df

def extract_ner(nlp, text):
    if not text or not isinstance(text, str):
        return []
    doc = nlp(text)
    return [ent.text for ent in doc.ents]

@timeit
def enrichment_NER(logger, nlp, df):
    logger.info("extaracting NER using spacy")
    ner_list = [extract_ner(nlp, t) for t in df['clean_text'].to_list()]

    logger.info("NER extraction complete")
    return df.with_columns(
        pl.Series("ner", ner_list)
    )

def extract_keywords(kw_model, text):
    try:
        kw = kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                top_n=5
        )
        return [k[0] for k in kw]
    except:
        return []
    
@timeit
def get_topics(logger, df, model):
    df = df.with_columns(
    pl.Series("keywords", [extract_keywords(model,x) for x in df["clean_text"]])
    )
    return df