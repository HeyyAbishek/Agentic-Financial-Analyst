 # 🏗️ System Architecture

The Agentic Financial Analyst is built using an **Event-Driven Microservice Architecture**. Tightly coupling a web frontend to a heavy LLM inference backend often results in HTTP timeouts, as multi-agent reasoning can take 30-60 seconds. To solve this, the system decouples the UI from the AI workers using a Redis message broker.



## Component Breakdown

### 1. The Client (Next.js / Vercel)
* **Role:** Handles user input (stock tickers) and provides real-time UI updates.
* **Mechanism:** Instead of waiting synchronously for a response, the client sends a `POST` request to the API Gateway, receives a `jobId`, and then initiates short-polling to check the job status.

### 2. The API Gateway (Node.js / Express)
* **Role:** The traffic controller. 
* **Mechanism:** It validates the incoming ticker, serializes the request into a job payload, and pushes it onto the **BullMQ** queue. It immediately responds to the client with an HTTP `202 Accepted` status.

### 3. The Message Broker (Redis / Upstash)
* **Role:** The state manager and buffer.
* **Mechanism:** Stores the BullMQ queue hashes. This ensures that if 10,000 users request an analysis simultaneously, the system will not crash; the queue simply scales, protecting the Python workers from being overwhelmed.

### 4. The AI Worker (Python / Render)
* **Role:** The execution engine powered by **LangGraph**.
* **Mechanism:** Continuously polls Redis for new jobs. Upon receiving a ticker, it orchestrates the multi-agent workflow:
  1. **Researcher Agent:** Fetches live metrics from the Finnhub API.
  2. **Bull & Bear Agents:** Synthesize the data in parallel, debating the bull and bear cases using the Llama-3.3-70b model (via Groq).
  3. **Judge Agent:** Evaluates the arguments, applies deterministic math guardrails to prevent hallucination, and writes the final JSON dossier back to Redis.

## Key Engineering Decisions

* **Asynchronous Processing:** Prevents Vercel's strict 10-second serverless function timeout from killing long-running LLM inferences.
* **Graceful Degradation:** The Python worker sanitizes corrupted or missing API data (e.g., replacing `$0` prices with `"Data Syncing"`) before feeding it to the LLM, preventing logical hallucinations.
* **Cold Start Mitigation:** Free-tier cloud containers sleep after 15 minutes of inactivity. To keep the UI snappy, the API Gateway fires an asynchronous, fire-and-forget HTTP `GET` webhook to the Python worker the exact millisecond a new job is queued, forcing the container to wake up while the user sees a loading screen.
