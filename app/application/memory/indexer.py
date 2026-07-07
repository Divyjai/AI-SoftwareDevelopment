from typing import Optional
from app.domain.memory.models import MemoryRecord

class MemoryIndexer:
    def prepare_for_embedding(self, record: MemoryRecord) -> Optional[str]:
        """
        Decides what text should be embedded for a given MemoryRecord.
        If it returns None, the record shouldn't be embedded.
        """
        # We want to embed the summary. For some types, we might combine metadata.
        if not record.summary or not record.summary.strip():
            return None
            
        parts = []
        if record.tags:
            parts.append(f"Tags: {', '.join(record.tags)}")
            
        parts.append(record.summary)
        
        return "\n".join(parts)
