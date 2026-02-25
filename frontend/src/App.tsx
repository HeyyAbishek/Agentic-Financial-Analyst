import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Search, Activity, AlertCircle, TrendingUp } from 'lucide-react';
import './App.css';

interface AnalysisResponse {
  jobId: string;
  ticker: string;
  status: string;
  message: string;
}

interface JobStatusResponse {
  jobId: string;
  state: 'waiting' | 'active' | 'completed' | 'failed' | 'delayed';
  result: string | null;
  error: string | null;
}

function App() {
  // --- PRODUCTION API URL ---
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api-gateway-analyst.onrender.com';
  
  const [ticker, setTicker] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);

  const analyzeStock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;

    setIsLoading(true);
    setError(null);
    setReport(null);
    setJobId(null);
    setPolling(false);

    try {
      // Hits the live Render API
      const response = await axios.post<AnalysisResponse>(`${API_BASE_URL}/api/v1/analyze`, {
        ticker: ticker.toUpperCase()
      });

      setJobId(response.data.jobId);
      setPolling(true);
    } catch (err) {
      setError('Failed to start analysis. The server might be waking up—please try again in a moment.');
      setIsLoading(false);
      console.error(err);
    }
  };

  useEffect(() => {
    let intervalId: any;

    if (polling && jobId) {
      intervalId = setInterval(async () => {
        try {
          const response = await axios.get<JobStatusResponse>(`${API_BASE_URL}/api/v1/analyze/${jobId}`);
          const { state, result, error: jobError } = response.data;

          if (state === 'completed' && result) {
            setReport(result);
            setIsLoading(false);
            setPolling(false);
          } else if (state === 'failed') {
            setError(jobError || 'Analysis failed unexpectedly.');
            setIsLoading(false);
            setPolling(false);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 3000); // Polling every 3 seconds for production
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [polling, jobId, API_BASE_URL]);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="logo-container">
          <TrendingUp className="logo-icon" />
          <div>
            <h1>Agentic Financial Analyst</h1>
            <p className="subtitle">AI-Powered Multi-Agent Investment Research</p>
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        <section className="search-section">
          <form onSubmit={analyzeStock} className="search-form">
            <div className="input-wrapper">
              <Search className="search-icon" />
              <input
                type="text"
                placeholder="Enter Stock Ticker (e.g., AAPL, NVDA, TSLA)"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <button type="submit" disabled={isLoading || !ticker}>
              {isLoading ? 'Analyzing...' : 'Analyze Stock'}
            </button>
          </form>
        </section>

        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p className="loading-text">
              <Activity className="pulse-icon" />
              AI Agents are debating... (Researcher → Bull → Bear → Judge)
            </p>
          </div>
        )}

        {error && (
          <div className="error-card">
            <AlertCircle className="error-icon" />
            <p>{error}</p>
          </div>
        )}

        {report && (
          <div className="report-card fade-in">
            <div className="report-header">
              <h2>Investment Thesis: {ticker.toUpperCase()}</h2>
              <span className="badge completed">Analysis Complete</span>
            </div>
            <div className="markdown-content">
              <ReactMarkdown>{report}</ReactMarkdown>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;