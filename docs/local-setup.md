# 💻 Local Setup Guide

Follow these steps to run the complete Agentic Financial Analyst microservice stack on your local machine.

## Prerequisites
Before you begin, ensure you have the following installed:
* [Node.js](https://nodejs.org/) (v18 or higher)
* [Python](https://www.python.org/downloads/) (v3.10 or higher)
* A Redis instance (either running locally via Docker, or a free cloud database like [Redis Cloud](https://redis.com/try-free/))
* API Keys for **Groq** and **Finnhub**.

## 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/agentic-financial-analyst.git](https://github.com/yourusername/agentic-financial-analyst.git)
cd agentic-financial-analyst
```

## 2. Setup the AI Worker (Backend)
This is the Python service that handles the LangGraph multi-agent workflow.

```bash
# Navigate to the worker directory
cd ai-worker

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside the `ai-worker` directory:
```env
REDIS_URL="redis://default:your_password@your_public_endpoint_url.redislabs.com:12345"
GROQ_API_KEY="gsk_your_groq_api_key"
FINNHUB_API_KEY="your_finnhub_api_key"
```

Start the worker:
```bash
python main.py
```
*The worker is now listening to your Redis queue.*

## 3. Setup the API Gateway & Client (Frontend)
Open a **new terminal window** and set up the Node.js/Next.js environment.

```bash
# Navigate to the frontend directory
cd api-gateway  # (or web-client, depending on your folder name)

# Install NPM packages
npm install
```

Create a `.env` file inside the `api-gateway` directory:
```env
REDIS_URL="redis://default:your_password@your_public_endpoint_url.redislabs.com:12345"
# Optional: Set this to your local Python worker URL for testing the wake-up ping
RENDER_WORKER_URL="http://localhost:8000" 
```

Start the development server:
```bash
npm run dev
```

## 4. Run an Analysis
1. Open your browser and navigate to `http://localhost:3000`.
2. Enter a ticker symbol (e.g., `MSFT`, `AAPL`, `NVDA`).
3. Watch the Node.js terminal queue the job, and the Python terminal execute the LangGraph workflow.
