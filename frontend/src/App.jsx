import { useState } from "react";
import axios from "axios";

export default function App() {
  const [url, setUrl] = useState("");
  const [operation, setOperation] = useState("thumbnail");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!url) {
      setError("Please enter a URL");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await axios.post("http://127.0.0.1:8000/process", {
        url,
        operation,
      });

      setResult(res.data.output_url);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="bg-black/40 backdrop-blur-xl border border-cyan-500/20 shadow-xl rounded-2xl p-8 w-full max-w-xl">

        <h1 className="text-3xl font-bold text-center mb-6 text-cyan-400">
          Media Processor ⚡
        </h1>

        {/* URL Input */}
        <input
          type="text"
          placeholder="Enter media URL..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="w-full p-3 rounded-lg bg-black border border-cyan-500/30 focus:outline-none focus:border-cyan-400 mb-4"
        />

        {/* Dropdown */}
        <select
          value={operation}
          onChange={(e) => setOperation(e.target.value)}
          className="w-full p-3 rounded-lg bg-black border border-cyan-500/30 mb-4"
        >
          <option value="thumbnail">Thumbnail</option>
          <option value="compress">Compress</option>
          <option value="extract_audio">Extract Audio</option>
        </select>

        {/* Button */}
        <button
          onClick={handleSubmit}
          className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-semibold py-3 rounded-lg transition"
        >
          Process Media
        </button>

        {/* Loading */}
        {loading && (
          <p className="text-center mt-4 text-cyan-300 animate-pulse">
            Processing...
          </p>
        )}

        {/* Error */}
        {error && (
          <p className="text-red-400 text-center mt-4">{error}</p>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 text-center">

            <p className="mb-2 text-cyan-400">Result:</p>

            {operation === "thumbnail" && (
              <img
                src={result}
                alt="thumbnail"
                className="rounded-lg border border-cyan-500/30"
              />
            )}

            {operation === "compress" && (
              <video
                src={result}
                controls
                className="w-full rounded-lg border border-cyan-500/30"
              />
            )}

            {operation === "extract_audio" && (
              <audio src={result} controls className="w-full" />
            )}

            <a
              href={result}
              target="_blank"
              rel="noreferrer"
              className="block mt-4 text-cyan-400 underline"
            >
              Open / Download
            </a>
          </div>
        )}
      </div>
    </div>
  );
}