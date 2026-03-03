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

// Routes
app.use('/api/v1', analyzeRoutes);

// Health check - This is the URL you will point your Cron-Job to!
app.get('/health', (req: Request, res: Response) => {
  res.status(200).send('ok'); 
});;

// Start server
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
