import logging, requests, time, os
from functools import wraps
import numpy as np
import polars as pl
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style
import xml.etree.ElementTree as ET 
from sentence_transformers import SentenceTransformer
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
    np.save(os.path.join(EMBEDDED_PATH, f"{book}_embeddings.npy"), embeddings)
    logger.info(f"Writing metadata to {book}_metadata.parquet")
    df.write_parquet(os.path.join(METADATA_PATH, f"{book}_metadata.parquet"))

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
