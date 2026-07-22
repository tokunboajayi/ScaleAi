# utils/queue.py
import asyncio
import uuid

class PipelineQueue:
    def __init__(self):
        self.batches = []

    async def push(self, batch):
        self.batches.append(batch)
        
    async def pop(self):
        if self.batches:
            return self.batches.pop(0)
        return None
