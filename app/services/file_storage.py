import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import shutil
from pathlib import Path
from app.core.config import settings


class FileStorageService:
    def __init__(self):
        self.base_dir = Path(settings.output_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.file_metadata: Dict[str, Dict] = {}
    
    def save_presentation(self, file_path: str, original_filename: str) -> Dict[str, str]:
        """Save a presentation file and return metadata"""
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Create new filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(original_filename).suffix
        new_filename = f"{file_id}_{timestamp}{file_extension}"
        
        # Move file to storage
        source_path = Path(file_path)
        target_path = self.base_dir / new_filename
        
        if source_path.exists():
            shutil.move(str(source_path), str(target_path))
        
        # Store metadata
        metadata = {
            "file_id": file_id,
            "original_filename": original_filename,
            "stored_filename": new_filename,
            "file_path": str(target_path),
            "file_size": target_path.stat().st_size if target_path.exists() else 0,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),  # 7 days expiry
            "download_count": 0,
            "is_active": True
        }
        
        self.file_metadata[file_id] = metadata
        
        return {
            "file_id": file_id,
            "download_url": f"/api/v1/download/{file_id}",
            "expires_at": metadata["expires_at"],
            "filename": original_filename
        }
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Get file metadata by ID"""
        return self.file_metadata.get(file_id)
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get file path by ID"""
        metadata = self.get_file_metadata(file_id)
        if metadata and metadata.get("is_active"):
            file_path = Path(metadata["file_path"])
            if file_path.exists():
                # Increment download count
                metadata["download_count"] += 1
                return str(file_path)
        return None
    
    def list_files(self) -> List[Dict]:
        """List all active files"""
        active_files = []
        for file_id, metadata in self.file_metadata.items():
            if metadata.get("is_active"):
                active_files.append({
                    "file_id": file_id,
                    "filename": metadata["original_filename"],
                    "created_at": metadata["created_at"],
                    "expires_at": metadata["expires_at"],
                    "download_count": metadata["download_count"],
                    "file_size": metadata["file_size"]
                })
        return sorted(active_files, key=lambda x: x["created_at"], reverse=True)
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID"""
        metadata = self.get_file_metadata(file_id)
        if metadata:
            file_path = Path(metadata["file_path"])
            if file_path.exists():
                file_path.unlink()
            
            # Mark as inactive
            metadata["is_active"] = False
            return True
        return False
    
    def cleanup_expired_files(self) -> int:
        """Clean up expired files"""
        current_time = datetime.now()
        expired_count = 0
        
        for file_id, metadata in list(self.file_metadata.items()):
            if metadata.get("is_active"):
                expires_at = datetime.fromisoformat(metadata["expires_at"])
                if current_time > expires_at:
                    self.delete_file(file_id)
                    expired_count += 1
        
        return expired_count
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        total_files = len([m for m in self.file_metadata.values() if m.get("is_active")])
        total_size = sum(m["file_size"] for m in self.file_metadata.values() if m.get("is_active"))
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_dir": str(self.base_dir)
        }


# Global file storage instance
file_storage = FileStorageService() 