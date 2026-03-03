import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import analyzeRoutes from './routes/analyze.routes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware - Updated for production stability
app.use(cors({
  origin: '*', // Allows all origins, including your Vercel deployment
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));

app.use(express.json());

// --- 1. BASE ROUTES ---

// Root route - Stops the "Cannot GET /" error
app.get('/', (req: Request, res: Response) => {
  res.status(200).send('API Gateway is Online and Active 🚀');
});

// Health check - Minimal response to stop "Response data too big" errors
app.get('/health', (req: Request, res: Response) => {
  res.status(200).send('ok'); 
});

// --- 2. API ROUTES ---
app.use('/api/v1', analyzeRoutes);

// --- 3. START SERVER ---
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
