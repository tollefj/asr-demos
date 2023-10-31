import jsonlines
import argparse
import re

import pandas as pd
import numpy as np
from faiss import Index
from autofaiss import build_index

from typing import Tuple


def rnd(num):
    return round(num * 2) / 2

def get_df(tv_show):
    base_path = "../data"
    speaker_path = f"{base_path}/diarized/{tv_show}.csv"
    transcr_path = f"{base_path}/transcriptions/{tv_show}.jsonl"

    df = pd.read_csv(speaker_path, header=None)
    df.columns = ["start", "end", "speaker"]
    def transform_speaker(speaker_str):
        return int(speaker_str.split("_")[2])
    df["speaker"] = df["speaker"].apply(transform_speaker)

    # round to nearest 0.5 seconds
    max_time = rnd(df.iloc[-1]["end"])

    # create a time series from 0 to max_time
    series = pd.Series(np.arange(0, max_time + 0.5, 0.5))
    series

    new_df = pd.DataFrame()
    new_df["time"] = series

    # DIARIZATION
    # for each speaker, find the time series indices that fall within the speaker's start-end time frame
    df_as_obj = df.to_dict(orient="records")
    for speaker in df_as_obj:
        speaker_id = speaker["speaker"]
        start = rnd(speaker["start"])
        end = rnd(speaker["end"])
        new_df[speaker_id] = new_df["time"].apply(lambda x: 1 if x >= start and x <= end else 0)

    # convert from detailed view to a single speaker col, -1 if there's no speaker
    new_df["speaker"] = -1
    for index, row in new_df.iterrows():
        for speaker_id in df["speaker"].unique():
            if row[speaker_id] == 1:
                new_df.at[index, "speaker"] = speaker_id
    new_df = new_df[["time", "speaker"]]

    # TRANSCRIPTIONS
    parsed = []
    with jsonlines.open(transcr_path) as reader:
        for obj in reader:
            timestamp = obj["timestamp"]
            txt = obj["text"]
            start, end = timestamp
            parsed.append({"start": start, "end": end, "text": txt})
    transcript_df = pd.DataFrame(parsed)
    transcript_df["text"] = transcript_df["text"].apply(lambda x: x.strip())
    # replace nan with max_end
    transcript_df["end"] = transcript_df["end"].fillna(max_time)
    # round all times to 0.5
    transcript_df["start"] = transcript_df["start"].apply(rnd)
    transcript_df["end"] = transcript_df["end"].apply(rnd)

    pattern = re.compile(r"\d+(?:,\d+)+")
    def filter_start(sent):
        sent = pattern.sub("", sent)
        return re.sub(r"^[^a-zA-Z0-9]+", "", sent)

    transcript_df["text"] = transcript_df["text"].apply(filter_start)

    # expand the start-end to 0.5 second intervals
    for index, row in transcript_df.iterrows():
        start = row["start"]
        end = row["end"]
        text = row["text"]
        for i in np.arange(start, end, 0.5):
            new_df.loc[new_df["time"] == i, "text"] = text
    new_df.fillna("", inplace=True)

    # create a mapping from text -> speaker
    text_to_speaker = {}
    for index, row in new_df.iterrows():
        speaker = row["speaker"]
        text = row["text"]

        if speaker == -1 or text == "":
            continue
        if text not in text_to_speaker:
            text_to_speaker[text] = {}
        if speaker not in text_to_speaker[text]:
            text_to_speaker[text][speaker] = 0
        text_to_speaker[text][speaker] += 1

    text_to_speaker = {k: max(v, key=v.get)
                    for k, v in sorted(text_to_speaker.items(),
                                        key=lambda item: sum(item[1].values()), reverse=True)}

    new_df["speaker"] = new_df["text"].apply(
        lambda x: text_to_speaker[x] if x in text_to_speaker else -1)
    
    new_df.drop_duplicates(subset="text", inplace=True)

    return new_df


def get_index_and_data(model, tv_show) -> Tuple[Index, pd.DataFrame]:
    """
    model: SentenceTransformer model
    """
    # parsed = []
    # print("Reading data")
    # with jsonlines.open(tv_show) as reader:
    #     for obj in reader:
    #         timestamp = obj["timestamp"]
    #         txt = obj["text"]
    #         start, end = timestamp
    #         parsed.append({"start": start, "end": end, "text": txt})
    # df = pd.DataFrame(parsed)
    df = get_df(tv_show)
    print("Encoding data")
    texts = list(set(df["text"].tolist()))
    embeddings = model.encode(texts, show_progress_bar=True)
    print("Building index")
    index, _ = build_index(embeddings, save_on_disk=False, verbose=0)
    print("Success")

    return index, df
