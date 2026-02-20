import { Router } from 'express';
import { analyzeStock } from '../controllers/analyze.controller';

const router = Router();

router.post('/analyze', analyzeStock);

export default router;
