import logging, requests, time, os, spacy
from functools import wraps
import numpy as np
import polars as pl
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style
import xml.etree.ElementTree as ET 
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bertopic import BERTopic
from keybert import KeyBERT
from typing import List, Dict
from ethics_bot.utils.common import *
from ethics_bot.utils.constants import *

app_name = "enrich_texts"
logger = get_logger(__file__, LOGGER_PATH / f'{app_name}')

df_bible = pl.read_parquet(os.path.join(METADATA_PATH, "bible_metadata.parquet"))
df_quran = pl.read_parquet(os.path.join(METADATA_PATH, "quran_english_metadata.parquet"))
df_gita = pl.read_parquet(os.path.join(METADATA_PATH, "gita_english_metadata.parquet"))

df_bible = add_sentiments(logger, df_bible)
df_quran = add_sentiments(logger, df_quran)
df_gita = add_sentiments(logger, df_gita)

nlp = spacy.load('en_core_web_sm', disable=['lemmatizer', 'tagger', 'parser'])

df_bible = enrichment_NER(logger, nlp, df_bible)
df_quran = enrichment_NER(logger, nlp, df_quran)
df_gita = enrichment_NER(logger, nlp, df_gita)

kw_model = KeyBERT(model='all-MiniLM-L6-v2')
df_bible = get_topics(logger, df_bible, kw_model)
df_quran = get_topics(logger, df_quran, kw_model)
df_gita = get_topics(logger, df_gita, kw_model)

df_bible.write_parquet(os.path.join(METADATA_PATH, "bible_metadata.parquet"))
df_quran.write_parquet(os.path.join(METADATA_PATH, "quran_english_metadata.parquet"))
df_gita.write_parquet(os.path.join(METADATA_PATH, "gita_english_metadata.parquet"))