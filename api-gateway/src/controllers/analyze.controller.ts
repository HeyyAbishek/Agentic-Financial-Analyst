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
