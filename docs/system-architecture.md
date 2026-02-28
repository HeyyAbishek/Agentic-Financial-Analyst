# System Architecture

The Agentic Financial Analyst utilizes a Hybrid-Cloud Microservice Architecture to handle long-running LLM inferences without blocking the user interface.

1.  **Client (Vercel/Next.js):** Takes the user's ticker input and initiates a polling request.
2.  **API Gateway (Node.js):** Pushes the research task to a Redis Message Queue.
3.  **Task Queue (Redis):** Manages state and pending AI workloads.
4.  **AI Worker (Render/Python):** * Pulls the task from Redis.
    * Triggers the **Researcher Agent** to ping the Finnhub API.
    * Triggers the **Bull and Bear Agents** in parallel (via LangGraph/Groq) to debate the data.
    * Triggers the **Judge Agent** to synthesize the final report.
5.  **Database/Cache:** Stores the final JSON dossier back in Redis for the frontend to retrieve.
