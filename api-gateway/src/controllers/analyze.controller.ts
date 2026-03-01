import { Request, Response } from 'express';
import { analysisQueue } from '../services/queue';

export const analyzeStock = async (req: Request, res: Response): Promise<void> => {
  const { ticker } = req.body;
  
  if (!ticker) {
    res.status(400).json({ error: 'Ticker is required' });
    return;
  }

  try {
    // 1. Explicitly clean the string to avoid hidden character issues
    const cleanTicker = ticker.toUpperCase().trim();
    
    // 2. FORCE BullMQ to treat the data as a plain object
    // Using Date.now() guarantees a fresh ID every single time
    const job = await analysisQueue.add(
      'analyze-stock', 
      { ticker: cleanTicker }, // Plain object payload
      { 
        jobId: `job-${cleanTicker}-${Date.now()}`,
        removeOnComplete: true,
        removeOnFail: false // Stop the noise of retries while we confirm this fix
      }
    );

    // This log is crucial—check your Node.js console for this!
    console.log(`Job Created: ${job.id} with ticker: ${cleanTicker}`);

    // 3. Wake up the Render Worker
    const RENDER_WORKER_URL = 'https://ai-worker-analyst.onrender.com';
    fetch(RENDER_WORKER_URL).catch((err: any) => {
        console.error("Worker ping failed/ignored:", err.message);
    });

    // 4. Respond to the frontend
    res.status(202).json({ 
      jobId: job.id, 
      ticker: cleanTicker,
      message: 'Analysis job successfully queued.'
    });
  } catch (error) {
    console.error('Error adding job to queue:', error);
    res.status(500).json({ error: 'Failed to queue analysis job' });
  }
};

export const getJobStatus = async (req: Request, res: Response): Promise<void> => {
  const { id } = req.params;

  try {
    const job = await analysisQueue.getJob(id as string);

    if (!job) {
      res.status(404).json({ error: 'Job not found' });
      return;
    }

    const state = await job.getState();
    const result = job.returnvalue;

    res.status(200).json({ 
      jobId: id, 
      state: state, 
      result: result || null 
    });
  } catch (error) {
    console.error(`Error fetching job status for ID ${id}:`, error);
    res.status(500).json({ error: 'Failed to fetch job status' });
  }
};
