import { Request, Response } from 'express';
import { analysisQueue } from '../services/queue';

export const analyzeStock = async (req: Request, res: Response): Promise<void> => {
  const { ticker } = req.body;
  
  if (!ticker) {
    res.status(400).json({ error: 'Ticker is required' });
    return;
  }

  try {
    const job = await analysisQueue.add('analyze-stock', { ticker });
    
    res.status(202).json({ 
      message: 'Analysis job queued successfully.',
      jobId: job.id,
      ticker,
      status: 'queued'
    });
  } catch (error) {
    console.error('Error adding job to queue:', error);
    res.status(500).json({ error: 'Failed to queue analysis job' });
  }
};
