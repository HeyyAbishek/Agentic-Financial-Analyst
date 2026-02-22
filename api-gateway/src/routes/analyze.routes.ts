import { Router } from 'express';
import { analyzeStock, getJobStatus } from '../controllers/analyze.controller';

const router = Router();

router.post('/analyze', analyzeStock);
router.get('/analyze/:id', getJobStatus);

export default router;
