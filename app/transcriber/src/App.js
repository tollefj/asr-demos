import React, { useState, useRef, useEffect } from 'react';
import debatten from "./assets/Debatten12okt.mp4";
import subtitle_json from "./assets/Debatten12oktSubtitle.js";
import { post } from "./api"

const HOST = "localhost"
// change to your local ip to access from other devices
// const HOST = "12.34.56.789"
const PORT = "8080"
const URL = `http://${HOST}:${PORT}`

function App() {
  const videoRef = useRef(null);
  const [query, setQuery] = useState('');
  const [currentTimestamp, setCurrentTimestamp] = useState(0);
  const [history, setHistory] = useState([]);
  const [infoMsg, setInfoMsg] = useState('');

  useEffect(() => {
    const video = videoRef.current;
    video.addEventListener("timeupdate", updateSubtitle);
    return () => {
      video.removeEventListener("timeupdate", updateSubtitle);
    };
  }, []);

  const getSubtitleAtTimestamp = (timestamp) => {
    for (const subtitle of subtitle_json) {
      const [start, end] = subtitle.timestamp;
      if (timestamp >= start && timestamp <= end) {
        return subtitle;
      }
    }
    return null;
  };

  const updateSubtitle = () => {
    const video = videoRef.current;
    const currentTime = video.currentTime;
    setCurrentTimestamp(currentTime);
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  }

  const searchVideos = async (e) => {
    const k = 3;
    // prevent page reload
    e.preventDefault();
    const res = await post(
      `${URL}/search`,
      JSON.stringify({ text: query, k }))

    // update infoMsg with number of results

    const timeStr = res.map(timestamp => {
      return `${parseFloat(timestamp["start"] / 1000).toFixed(2)
        }-->${parseFloat(timestamp["end"] / 1000).toFixed(2)
        }`
    });
    const historyString = `${query} (${timeStr})`
    setHistory([historyString, ...history])

    console.log(res)
    for (const timestamp of res) {
      const start = timestamp["start"]
      const end = timestamp["end"] + 1.5
      const duration = end - start
      console.log(start)
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

  const currentSubtitle = getSubtitleAtTimestamp(currentTimestamp);

  return (
    <div className="App">
      <header className="App-header">
        <h1>SCRIBE - NorwAI demo</h1>
        <h5>
          Machine transcription of Norwegian conversational speech
          <a href="https://scribe-project.github.io/">scribe-project.github.io</a>
        </h5>
      </header>
      <div className="content" style={{
        "display": "flex",
        "flexDirection": "row",
        "justifyContent": "space-between",
      }}>
        <div className="video-container">
          <video ref={videoRef} src={debatten} controls />
          <div id="subtitle">
            {currentSubtitle && <p>{currentSubtitle.text}</p>}
          </div>
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
        </div>
      </div>
    </div>
  );
}

export default App;
