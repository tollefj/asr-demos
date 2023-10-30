import React, { useState, useRef, useEffect } from 'react';
import { post } from "./api"

const HOST = "localhost"
// change to your local ip to access from other devices
// const HOST = "12.34.56.789"
const PORT = "8080"
const URL = `http://${HOST}:${PORT}`

// UI element to show 4 available TV programs to choose from, based on a list of IDs.
// It should be a select element with 4 options, with only text
const TVProgramSelector = ({ tvPrograms, onChange }) => {
  return (
    <select onChange={onChange} defaultValue="">
      <option value="" disabled>Select TV program</option>
      {tvPrograms.map((tvProgram, index) => (
        <option key={index} value={tvProgram}>{tvProgram.replace(".jsonl", "")}</option>
      ))}
    </select>
  );
}

function App() {
  const videoRef = useRef(null);
  const [query, setQuery] = useState('');
  const [currentTimestamp, setCurrentTimestamp] = useState(0);
  const [history, setHistory] = useState([]);
  const [validTranscriptions, setValidTranscriptions] = useState([]);
  const [selectedTranscription, setSelectedTranscription] = useState(null);
  const [currentSubtitle, setCurrentSubtitle] = useState("");
  const [k, setK] = useState(3);
  const [ready, setReady] = useState(false);

  // fetch valid transcriptions from /transcriptions get endpoint
  useEffect(() => {
    const fetchTranscriptions = async () => {
      const res = await fetch(`${URL}/transcriptions`);
      const data = await res.json();
      console.log("fetched transcriptions", data)
      setValidTranscriptions(data);
    }
    fetchTranscriptions();
  }, [])

  useEffect(() => {
    const updateSubtitle = async () => {
      const video = videoRef.current;
      const currentTime = video.currentTime;
      if (currentTime - currentTimestamp > 0.3) {
        const res = await post(
          `${URL}/subtitle`,
          JSON.stringify({ timestamp: currentTime }))
        console.log(res)
        setCurrentTimestamp(currentTime);
        setCurrentSubtitle(res)
      }
    };
    const video = videoRef.current;
    if (ready) {
      video.addEventListener("timeupdate", updateSubtitle);
      return () => {
        video.removeEventListener("timeupdate", updateSubtitle);
      };
    }
  }, [currentTimestamp, setCurrentTimestamp, videoRef, ready]);

  const handleTvShowSelect = async (e) => {
    setReady(false)
    const selectedTvProgram = e.target.value;
    setSelectedTranscription(selectedTvProgram);
    // send a post request to /update with the selected program
    const res = await post(`${URL}/update`, JSON.stringify({ path: selectedTvProgram }))
    if (res.status === "ok") {
      setReady(true);
    }
  }

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  }

  const searchVideos = async (e) => {
    e.preventDefault();
    const res = await post(
      `${URL}/search`,
      JSON.stringify({ text: query, k }))

    const timeStr = res.map(timestamp => {
      return `${parseFloat(timestamp["start"]).toFixed(2)}-->${parseFloat(timestamp["end"]).toFixed(2)}`
    });

    const historyString = `${query} (${timeStr})`
    setHistory([historyString, ...history])

    for (const timestamp of res) {
      const start = timestamp["start"]
      const end = timestamp["end"] + 1.5
      const duration = end - start
      videoRef.current.currentTime = start;
      videoRef.current.play();
      await new Promise(resolve => setTimeout(resolve, 1000 * duration));
    }
  };

  const handleHistoryClick = (historyString) => {
    const timestamps = historyString.match(/\d+\.\d+-->\d+\.\d+/g);

    if (timestamps) {
      const [start, end] = timestamps[0].split("-->");
      videoRef.current.currentTime = parseFloat(start) * 1000;
      videoRef.current.play();
    }
  }

  const videoPath = selectedTranscription ? require(`./assets/${selectedTranscription.replace(".jsonl", ".mp4")}`) : null;

  return (
    <div className="App">
      <header className="App-header">
        <div id="header-left">
          <h1>Interact with TV programs</h1>
          <h5>a SCRIBE demo at NorwAI</h5>
        </div>
        <div id="header-right">
          <img width={128} src={require("./assets/qr_scribe.png")} alt="QR code" />
          <a href="https://scribe-project.github.io/">scribe-project.github.io</a>
        </div>
      </header>
      <div className="content" style={{
        "display": "flex",
        "flexDirection": "row",
        "justifyContent": "space-between",
      }}>
        <div className="video-container">
          {(videoPath && ready) ? (
            <>
              <video ref={videoRef} src={videoPath} type="video/mp4" controls />
              <div id="subtitle">
                {currentSubtitle && <p>{currentSubtitle.text}</p>}
              </div>
            </>
          ) : (
            <>
              <h2>Waiting for transcription backend...</h2>
            </>
          )}
        </div>
        <div className="search-history-container">
          <form onSubmit={searchVideos}>
            <input type="text" value={query} onChange={handleQueryChange} required />
            <button type="submit" disabled={!query}>Transcription search</button>
          </form>
          <div className="search-history">
            {history.map((item, index) => (
              <div key={index} className="search-history-item" onClick={() => handleHistoryClick(item)}>
                <p>{item}</p>
                <hr />
              </div>
            ))}
          </div>
          <div className="file-selector">
            <TVProgramSelector tvPrograms={validTranscriptions} onChange={handleTvShowSelect} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
