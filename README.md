# Agentic Financial Analyst - Autonomous AI Investment Committee

![Status: Production](https://img.shields.io/badge/Status-Production-brightgreen) ![Architecture: Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-blue) ![LLM: Llama--3.3--70b](https://img.shields.io/badge/LLM-Llama--3.3--70b-orange) ![API: Finnhub](https://img.shields.io/badge/API-Finnhub-yellow)

**Agentic Financial Analyst** is a production-grade AI platform that performs autonomous fundamental stock analysis. It solves the "LLM Hallucination" problem by using deterministic math guardrails, real-time market data injection, and a specialized multi-agent workflow to simulate a real-world investment committee.

<img width="1846" height="904" alt="Screenshot 2026-03-01 001859" src="https://github.com/user-attachments/assets/b5b52ae3-b1fa-41de-8832-0625c2508871" />

## 🚀 Live Demo


https://github.com/user-attachments/assets/08f85afc-6104-4343-9065-abee9f11497b



👉 **[View Live Deployment](https://your-deployment-link.vercel.app)** *(Try searching for `AAPL`, `NVDA`, or `GME` to see the agents debate!)*

## 📚 Documentation

I have documented the engineering decisions and system design in detail:

* **[System Architecture](./docs/system-architecture.md):** Breakdown of the Hybrid Cloud setup (Vercel + Render), Multi-Agent State Management, and API routing.
* **[Technical Challenges](./docs/technical-challenges.md):** Deep dive into preventing AI logic hallucinations, handling missing API data via Graceful Degradation, and global currency normalization.
* **[Local Setup Guide](./docs/local-setup.md):** Instructions to run the multi-agent worker and frontend locally.

## ✨ Key Features

* **Multi-Agent Workflow:** Utilizes LangGraph to coordinate four distinct AI personas: a **Researcher** (Data Retrieval), a **Bull** (Optimist), a **Bear** (Pessimist), and a **Judge** (Synthesizer).
* **Hallucination Prevention:** Strict prompt engineering and "Math Guardrails" force the LLM to calculate deterministic percentages rather than inventing fake market crashes.
* **Graceful Degradation:** Smart fallback logic handles unreliable API endpoints (e.g., replacing corrupted `$0` prices with "Data Syncing") to keep the AI's logic intact.
* **Global Currency Normalization:** Dynamically scales market caps and standardizes local currencies (like TWD and INR) into readable USD equivalents for global consistency.
* **Real-Time Data Injection:** Integrates the **Finnhub API** for live quotes, P/E ratios, and 52-week highs to ground the AI's analysis in absolute reality.
* **Asynchronous AI Queues:** Uses **Redis** and a hybrid deployment (Node.js on Vercel, Python AI Workers on Render) to handle long-running AI inference tasks without frontend timeouts.

---
Built by **Abishek Jha**
