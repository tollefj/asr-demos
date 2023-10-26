from transformers import pipeline
import os

asr = pipeline(
    "automatic-speech-recognition",
    "NbAiLab/nb-whisper-base-beta"
)
fp = "../mp3s-split/harstad/kommunestyremote2020/segment_1.mp3"
res = asr(
    fp,
    generate_kwargs={'task': 'transcribe', 'language': 'no'},
    return_timestamps=True,
)
print(res)
chunk_dict = res["chunks"]
import json
output_fp = "output.json"
# remove the file if it exists:
if os.path.exists(output_fp):
    os.remove(output_fp)

with open(output_fp, "w") as f:
    json.dump(chunk_dict, f)