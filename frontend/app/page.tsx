"use client"; //making use of useState

import { useState } from "react";

const API_URL = "http://localhost:8000"; //backend API running on port 8000

export default function Home() {
  const [url, setUrl] = useState(""); //url for youtube video put in search
  const [environment, setEnvironment] = useState("FOREST"); //environment setting selection
  const [videoUrl, setVideoUrl] = useState<string | null>(null); //attach to url to load video
  const [downloading, setDownloading] = useState(false); //currently downloading
  const [filename, setFilename] = useState<string | null>(null); //set filename for analyser
  const [analyzing, setAnalyzing] = useState(false); //currently analysing the video
  const [results, setResults] = useState<any | null>(null); //results received from analysis

  async function handleDownload() {
    if (!url) return; // make sure a url is entered before download proceeds
    setDownloading(true); //it is now downloading
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("url", url); //api funciton arg is url

      //post request to /download  wiht {url: ...}
      const response = await fetch(`${API_URL}/download`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setVideoUrl(`${API_URL}${data.video_url}`); //assigns video url
      setFilename(data.filename);
    } catch (error) {
      console.error("Download failed:", error);
    } finally {
      setDownloading(false);
    }
  }

  async function handleAnalyze() {
    if (!filename) return; //Analysis cant happen until video has been downlaoded
    setAnalyzing(true);

    try {
      //set arguement values to put into json to send
      const formData = new FormData();
      formData.append("filename", filename);
      formData.append("environment", environment);

      //send request to analyse
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("Analysis results:", data); 
      setResults(data);//store the event data
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setAnalyzing(false);
    }
  }

  //I want to convert time that is a number to string to make the timestamp look nice
  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toFixed(1).padStart(4, "0")}`;
  }

  return (
    <main className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-5xl mx-auto flex flex-col gap-8">

        {/* Top section — controls and video */}
        <div className="flex gap-8">

          {/* Left side — controls */}
          <div className="w-full max-w-md">
            <h1 className="text-4xl font-bold text-gray-100 mb-2">Wildlife Monitor</h1>
            <p className="text-gray-400 mb-8">Monitor wildlife activity from video footage</p>
            {/* Youtube download controls */}
            <div className="flex flex-col gap-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Paste a YouTube URL..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1 border border-gray-700 rounded-lg p-3 text-lg bg-gray-900 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500"
                />
                <button
                  onClick={handleDownload}
                  disabled={downloading || !url}
                  className="border border-gray-600 bg-gray-800 text-gray-100 rounded-lg px-5 text-lg font-medium hover:bg-gray-700 transition-colors shadow-sm whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {downloading ? "Downloading..." : "Download"}
                </button>
              </div>
              {/* Environment controls */}
              <div className="flex gap-2">
                <select
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value)}
                  className="flex-1 border border-gray-700 rounded-lg p-3 text-lg bg-gray-900 text-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  <option value="FOREST">Forest</option>
                  <option value="WETLAND">Wetland</option>
                  <option value="SAVANNA">Savanna</option>
                  <option value="ARCTIC">Arctic</option>
                  <option value="URBAN">Urban</option>
                  <option value="MOUNTAIN">Mountain</option>
                </select>
                <button
                  onClick={handleAnalyze}
                  disabled={!filename || analyzing}
                  className="border border-gray-600 bg-gray-800 text-gray-100 rounded-lg px-5 text-lg font-medium hover:bg-gray-700 transition-colors shadow-sm whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {analyzing ? "Analyzing..." : "Analyze"}
                </button>
              </div>
            </div>
          </div>

          {/* Right side — video player */}
          <div className="flex-1 flex items-center justify-center border border-gray-700 rounded-lg bg-gray-900 min-h-[300px]">
            {videoUrl ? (
              <video src={videoUrl} controls className="w-full rounded-lg" />
            ) : (
              <p className="text-gray-500"></p>
            )}
          </div>
        </div>

        {/* Results section - when results genreated, it gets produced*/}
        {results && (
          <div className="flex flex-col gap-6">

            {/* Summary stats */}
            <div className="flex gap-4">
              <div className="flex-1 border border-gray-700 rounded-lg bg-gray-900 p-4">
                <p className="text-gray-400 text-sm">Animals Seen</p>
                <p className="text-3xl font-bold text-gray-100">{results.animal_count}</p>
              </div>

              <div className="flex-1 border border-gray-700 rounded-lg bg-gray-900 p-4">
                <p className="text-gray-400 text-sm">Species</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {Object.entries(results.species).map(([name, count]) => (
                    <span key={name} className="text-gray-100 bg-gray-800 rounded px-2 py-1 text-sm">
                      {name} ({count as number})
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex-1 border border-gray-700 rounded-lg bg-gray-900 p-4">
                <p className="text-gray-400 text-sm">Dominant Sounds</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {results.dominant_sounds.map(([label, score]: [string, number]) => (
                    <span key={label} className="text-gray-100 bg-gray-800 rounded px-2 py-1 text-sm">
                      {label}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Event timeline */}
            <div className="border border-gray-700 rounded-lg bg-gray-900 p-6">
              <h2 className="text-xl font-bold text-gray-100 mb-6">Event Timeline</h2>

              <div className="relative border-l border-gray-700 ml-4">
                {results.events.map((event: any, i: number) => (
                  <div key={i} className="mb-6 ml-6 relative">
                    {/* dot on the timeline */}
                    <div className="absolute -left-[9.5px] top-1 w-2 h-2 rounded-full bg-gray-500 border-2 border-gray-900" />

                    <p className="text-gray-400 text-sm">{formatTime(event.timestamp)}</p>
                    <p className="text-gray-100 font-medium">{event.description}</p>
                    <span className="text-xs text-gray-500 bg-gray-800 rounded px-2 py-0.5">
                      {event.event_type}
                    </span>
                    {event.confidence > 0 && (
                      <span className="text-xs text-gray-500 ml-2">
                        {(event.confidence * 100).toFixed(0)}% confidence
                      </span>
                    )}
                    {/* Attach screenshot to the timeline */}
                    {event.frame_url && (
                      <img
                        src={`${API_URL}${event.frame_url}`}
                        alt={event.description}
                        className="mt-2 rounded border border-gray-700 max-w-xs"
                        onError={(e) => (e.currentTarget.style.display = "none")}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

      </div>
    </main>
  );
}
