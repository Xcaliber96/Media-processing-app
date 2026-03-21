import { useState } from "react";
import axios from "axios";

export default function App() {
  console.log("API URL:", import.meta.env.VITE_API_URL);
  const [url, setUrl] = useState("");
  const [operation, setOperation] = useState("thumbnail");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!url) {
      setError("System prompt: Please enter a valid URL.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await axios.post("http://localhost:8000/process", {
        url,
        operation,
      });

      setResult(res.data.output_url);
    } catch (err) {
      setError(err.response?.data?.detail || "System error: Processing failed.");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-black font-mono text-zinc-300">
      <div className="bg-[#0a0a0a] border border-zinc-800 shadow-2xl rounded-sm p-8 w-full max-w-xl">
        
        <h1 className="text-xl tracking-widest uppercase font-semibold text-center mb-8 text-emerald-500/80">
          Media Processor
        </h1>

        
        <input
          type="text"
          placeholder="Enter media URL..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="w-full p-3 bg-[#111] border border-zinc-800 text-emerald-400 placeholder-zinc-600 focus:outline-none focus:border-emerald-500/40 focus:bg-[#151515] transition-colors mb-4 rounded-none"
        />

        
        <select
          value={operation}
          onChange={(e) => setOperation(e.target.value)}
          className="w-full p-3 bg-[#111] border border-zinc-800 text-zinc-300 focus:outline-none focus:border-emerald-500/40 focus:bg-[#151515] transition-colors mb-6 rounded-none appearance-none"
        >
          <option value="thumbnail">Generate Thumbnail</option>
          <option value="compress">Compress Media</option>
          <option value="extract_audio">Extract Audio</option>
        </select>

       
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-[#0a0a0a] border border-emerald-500/30 hover:border-emerald-500/80 hover:bg-emerald-950/20 text-emerald-500/90 tracking-widest uppercase text-sm py-3 transition-all duration-300 rounded-none disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Processing..." : "Initialize"}
        </button>

    
        {loading && (
          <p className="text-center mt-6 text-emerald-500/50 text-sm animate-pulse tracking-widest uppercase">
            Awaiting response...
          </p>
        )}

        
        {error && (
          <p className="text-red-500/80 text-center mt-6 text-sm tracking-wide">
            {error}
          </p>
        )}

       
        {result && (
          <div className="mt-8 pt-6 border-t border-zinc-800 text-center">
            <p className="mb-4 text-emerald-500/60 text-xs tracking-widest uppercase">
              Output Generated
            </p>

            {operation === "thumbnail" && (
              <img
                src={result}
                alt="thumbnail"
                className="mx-auto border border-zinc-800 opacity-90 hover:opacity-100 transition-opacity"
              />
            )}

            {operation === "compress" && (
              <video
                src={result}
                controls
                className="w-full border border-zinc-800 bg-black"
              />
            )}

            {operation === "extract_audio" && (
              <audio 
                src={result} 
                controls 
                className="w-full opacity-80" 
              />
            )}

            <a
              href={result}
              target="_blank"
              rel="noreferrer"
              className="inline-block mt-6 px-4 py-2 text-xs tracking-widest uppercase text-zinc-400 hover:text-emerald-400 border border-transparent hover:border-zinc-800 transition-all"
            >
              [ Access File ]
            </a>
          </div>
        )}
      </div>
    </div>
  );
}