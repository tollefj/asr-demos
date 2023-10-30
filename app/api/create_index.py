import jsonlines
import argparse

import numpy as np
import pandas as pd
from faiss import Index
from autofaiss import build_index

from typing import Tuple

def segment_sentences(start, end, txt):
    if "." not in txt:
        return [{"start": start, "end": end, "text": txt.strip()}]
    sentences = [s.strip() for s in txt.split(".") if len(s.strip()) > 0]
    n_sents = len(sentences)
    segments = []
    for _, sentence in enumerate(sentences):
        segments.append({"start": start, "end": end, "text": sentence})
    return segments

def get_index_and_data(model, jsonl_data) -> Tuple[Index, pd.DataFrame]:
    """
    model: SentenceTransformer model
    """
    parsed = []
    print("Reading data")
    with jsonlines.open(jsonl_data) as reader:
        for obj in reader:
            timestamp = obj["timestamp"]
            txt = obj["text"]
            start, end = timestamp
            segments = segment_sentences(start, end, txt)
            segments = [s for s in segments if len(s["text"].split()) > 2]
            parsed.extend(segments)

    df = pd.DataFrame(parsed)
    print("Encoding data")
    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
    print("Building index")
    index, _ = build_index(embeddings, save_on_disk=False, verbose=0)
    print("Success")

    return index, df
