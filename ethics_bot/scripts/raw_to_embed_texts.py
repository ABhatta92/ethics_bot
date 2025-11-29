import logging, requests, time, os
from functools import wraps
import numpy as np
import polars as pl
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style
import xml.etree.ElementTree as ET 
from sentence_transformers import SentenceTransformer
from ethics_bot.utils.constants import *
from ethics_bot.utils.common import *
from ethics_bot.scripts.process_texts import *

app_name = "raw_to_embed_texts"
logger = get_logger(__file__, LOGGER_PATH / f'{app_name}')

df_bible = process_bible(logger, BIBLE_PATH)
df_bible.head()
clean_and_embed_text(logger, df_bible, 'bible')
df_quran = process_quran(logger, QURAN_PICKTHALL_PATH)
df_quran.head()
clean_and_embed_text(logger, df_quran, 'quran_english')
df_gita = process_gita()
df_gita.head()
clean_and_embed_text(logger, df_gita, 'gita_english')