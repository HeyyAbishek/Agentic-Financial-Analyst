import { Redis } from 'ioredis';
import { Queue } from 'bullmq';
import dotenv from 'dotenv';

dotenv.config();

// Fallback to localhost ONLY if the environment variable is missing
const redisConnection = new Redis(process.env.REDIS_URL || 'redis://127.0.0.1:6379', {
    maxRetriesPerRequest: null,
    tls: process.env.REDIS_URL?.startsWith('rediss://') ? {} : undefined
});

// Pass that specific connection into your BullMQ queue
export const analysisQueue = new Queue('analysis-queue', {
    connection: redisConnection
});