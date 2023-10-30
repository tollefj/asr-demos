import jsonlines
import argparse

import pandas as pd
from faiss import Index
from autofaiss import build_index

from typing import Tuple

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
            parsed.append({"start": start, "end": end, "text": txt})

    df = pd.DataFrame(parsed)
    print("Encoding data")
    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
    print("Building index")
    index, _ = build_index(embeddings, save_on_disk=False, verbose=0)
    print("Success")

    return index, df
