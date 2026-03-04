import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import analyzeRoutes from './routes/analyze.routes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// --- 1. HEALTH CHECK (Minimal for Cron) ---
app.get('/health', (req: Request, res: Response) => {
  // .end() sends 0 bytes. Perfect for cron-job.org
  res.status(200).end(); 
});

// Middleware - Production Stability
app.use(cors({
  origin: '*', 
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));

app.use(express.json());

// --- 2. BASE ROUTES ---
app.get('/', (req: Request, res: Response) => {
  res.status(200).send('API Gateway is Online and Active 🚀');
});

// --- 3. API ROUTES ---
app.use('/api/v1', analyzeRoutes);

// --- 4. START SERVER ---
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
