import flask
from flask_cors import CORS, cross_origin

import json
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

app = flask.Flask(__name__)
CORS(app)

FRONTEND_HOST = "localhost"
FRONTEND_PORT = 3000
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['CORS_ORIGINS'] = '*'


index = faiss.read_index("knn.index", faiss.IO_FLAG_MMAP | faiss.IO_FLAG_READ_ONLY)
print(f"Loading s-bert model")
model = SentenceTransformer("NbAiLab/nb-sbert-base")
df = pd.read_csv("debatten.csv")
print(df.head())

def query(q, K=1):
    emb = model.encode([q], show_progress_bar=False)
    _, matches = index.search(emb, K)
    res = df.iloc[matches[0]]
    # from the start and end columns
    # return a list of objects with start and end
    return [
        {
            "start": row["start"],
            "end": row["end"]
        }
        for _, row in res.iterrows()
    ]

def make_response(error: bool, message: str) -> flask.Response:
    return flask.jsonify({ "error": error, "message": message })

@app.route('/status')
def health_check() -> str:
    return f"app is running on {SERVER_HOST}:{SERVER_PORT}"

default_timestamps = [1,2,3]

@app.route('/search', methods=['POST'])
def predictions() -> flask.Response:
    text = flask.request.json.get('text')
    k = flask.request.json.get('k')
    print(text)
    # find the top K similar sentences from the computed index
    # return a list of timestamps (start, end) for the matched sentences in the dataframe
    query_result = query(text, K=k)
    print("result", query_result)
    return flask.jsonify(query_result)

# also set up a GET for /search
@app.route('/search', methods=['GET'])
def predictions_all() -> flask.Response:
    return flask.jsonify(default_timestamps)

app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True, threaded=True)

