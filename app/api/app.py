import flask
from flask_cors import CORS
import os
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from create_index import get_index_and_data
<<<<<<< Updated upstream
=======
import numpy as np
from transcriber import WhisperTranscriber
>>>>>>> Stashed changes

app = flask.Flask(__name__)
CORS(app)

FRONTEND_HOST = "localhost"
FRONTEND_PORT = 3000
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

app.config['CORS_HEADERS'] = 'Content-Type'


SBERT_MODEL = "NbAiLab/nb-sbert-base"
# SBERT_MODEL = "intfloat/multilingual-e5-base"
WHISPER_MODEL = "NbAiLab/nb-whisper-small-beta"

def download(url):
    print(f"Downloading {url}"")
    cmd = "download_and_segment.sh"
    subprocess.run([cmd, url], check=True)
    out_dir = "../data/transcriptionsV2/"
    print(f"Transcribing {url} to {out_dir}"")
    transcriber = WhisperTranscriber(model=WHISPER_MODEL, out_dir=out_dir, audio_file=url)




class DataStore:
    def __init__(self):
        print(f"Loading s-bert model")
        self.model = SentenceTransformer("NbAiLab/nb-sbert-base")
        self.index: faiss.Index = None
        self.df: pd.DataFrame = None

        self.data_folder = "../data/transcriptions/"
        self.valid_transcriptions = [
            f for f in os.listdir(self.data_folder) if f.endswith(".jsonl")
        ]

    def update(self, jsonl_path):
        path = os.path.join(self.data_folder, jsonl_path)
        self.index, self.df = get_index_and_data(self.model, path)

    # a function to retrieve the corresponding subtitle from a current timestamp (start)
    # the df has the following columns: start, end, text
    def get_subtitle(self, timestamp, buffer=1):
        if self.df is None:
            return None
        for i, row in self.df.iterrows():
            if row["start"] - buffer <= timestamp and timestamp <= row["end"]:
                delta = abs(timestamp - row["start"])
                if delta > 10 or i >= len(self.df):
                    return None
                return row["text"]
        
    def download(self, url):
        cmd = "download_and_segment.sh"
        subprocess.run([cmd, url], check=True)
        
    def query(self, q, k=1):
        emb = self.model.encode([q], show_progress_bar=False)
        _, matches = self.index.search(emb, k)
        res = self.df.iloc[matches[0]]
        return [
            {
                "start": row["start"],
                "end": row["end"]
            }
            for _, row in res.iterrows()
        ]

datastore = DataStore()

@app.route('/status')
def health_check() -> str:
    return f"app is running on {SERVER_HOST}:{SERVER_PORT}"

@app.route('/update', methods=['POST'])
def update() -> flask.Response:
    jsonl_path = flask.request.json.get('path')
    datastore.update(jsonl_path)
    return flask.jsonify({"status": "ok"})

@app.route('/transcriptions')
def get_valid() -> flask.Response:
    return flask.jsonify(datastore.valid_transcriptions)

@app.route('/search', methods=['POST'])
def predictions() -> flask.Response:
    text = flask.request.json.get('text')
    k = flask.request.json.get('k')
    print(text)
    query_result = datastore.query(q=text, k=k)
    print("result", query_result)
    return flask.jsonify(query_result)

@app.route('/subtitle', methods=['POST'])
def get_subtitle() -> flask.Response:
    timestamp = flask.request.json.get('timestamp')
    print(f"timestamp: {timestamp}")
    subtitle = datastore.get_subtitle(timestamp)
    return flask.jsonify({"text": subtitle})

app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True, threaded=True)

