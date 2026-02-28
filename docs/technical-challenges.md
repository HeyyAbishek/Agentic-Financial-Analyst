# Technical Challenges & Solutions

Building a deterministic output from a probabilistic LLM required solving several critical data and logic issues.

### 1. The "Logic Hallucination" Problem (The 81% Crash Bug)
* **Challenge:** The LLM (acting as the Judge) would often see a high P/E ratio and automatically invent a narrative to justify a "Bearish" stance, famously hallucinating that a stock crashed 81% from its 52-week high, despite the math proving otherwise.
* **Solution:** Implemented **"Math Guardrails"** via prompt engineering. I injected strict deterministic instructions (`DATA INTEGRITY RULE: Calculate percentage drop exactly using (High - Price) / High`) and forced the AI to acknowledge the real data points before writing its thesis.

### 2. The "Zero-Price Panic" (Graceful Degradation)
* **Challenge:** Free-tier financial APIs occasionally throttle or drop connections, returning a `0` or `null` for a stock price. When fed into the AI, the agents would panic and declare the company bankrupt.
* **Solution:** Built a **Graceful Degradation** fallback in the Python Researcher agent. If the API returns garbage data (like a `$0` price or the year `2025` as a 52-week high), the script sanitizes the payload into string tags like `"Data Syncing"`. This signals the LLM to exercise caution rather than making catastrophic assumptions.

### 3. Global Currency Scale Mismatches
* **Challenge:** International stocks (like TSMC) report Market Capitalization in local currencies (TWD), resulting in raw numbers in the millions of millions. The AI would read "51 Trillion" next to a "$372" stock price and generate confusing valuation reports.
* **Solution:** Implemented a **Currency Normalization layer** that calculates USD equivalents for specific international tickers and accurately labels local units, ensuring the AI maintains context across global exchanges.
