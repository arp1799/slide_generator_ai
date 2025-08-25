import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import shutil
from pathlib import Path
from app.core.config import settings


class FileStorageService:
    def __init__(self):
        self.base_dir = Path(settings.output_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.metadata_file = self.base_dir / "file_metadata.json"
        self.file_metadata: Dict[str, Dict] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata from JSON file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.file_metadata = json.load(f)
                print(f"📁 Loaded {len(self.file_metadata)} file metadata entries from {self.metadata_file}")
            else:
                print(f"📁 No existing metadata file found at {self.metadata_file}")
        except Exception as e:
            print(f"⚠️ Error loading metadata: {e}")
            self.file_metadata = {}
    
    def _save_metadata(self):
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.file_metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving metadata: {e}")
    
    def _rebuild_metadata_from_files(self):
        """Rebuild metadata by scanning existing files in storage directory"""
        print("🔍 Rebuilding metadata from existing files...")
        rebuilt_count = 0
        
        for file_path in self.base_dir.glob("*.pptx"):
            if file_path.name == "file_metadata.json":
                continue
                
            # Try to extract file_id from filename (format: {file_id}_{timestamp}.pptx)
            filename_parts = file_path.stem.split('_')
            if len(filename_parts) >= 2:
                try:
                    file_id = filename_parts[0]
                    timestamp = '_'.join(filename_parts[1:])
                    
                    # Check if this file_id already exists in metadata
                    if file_id not in self.file_metadata:
                        # Create metadata entry
                        metadata = {
                            "file_id": file_id,
                            "original_filename": f"presentation_{file_id}.pptx",
                            "stored_filename": file_path.name,
                            "file_path": str(file_path),
                            "file_size": file_path.stat().st_size if file_path.exists() else 0,
                            "created_at": datetime.now().isoformat(),  # Approximate
                            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
                            "download_count": 0,
                            "is_active": True
                        }
                        self.file_metadata[file_id] = metadata
                        rebuilt_count += 1
                        print(f"   Rebuilt metadata for: {file_id}")
                except Exception as e:
                    print(f"   ⚠️ Error processing file {file_path.name}: {e}")
        
        if rebuilt_count > 0:
            self._save_metadata()
            print(f"✅ Rebuilt metadata for {rebuilt_count} files")
    
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
        self._save_metadata()  # Persist to disk
        
        return {
            "file_id": file_id,
            "download_url": f"/api/v1/download/{file_id}",
            "expires_at": metadata["expires_at"],
            "filename": original_filename
        }
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Get file metadata by ID"""
        metadata = self.file_metadata.get(file_id)
        
        # If metadata not found, try to rebuild from files
        if not metadata:
            self._rebuild_metadata_from_files()
            metadata = self.file_metadata.get(file_id)
        
        return metadata
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get file path by ID"""
        metadata = self.get_file_metadata(file_id)
        if metadata and metadata.get("is_active"):
            file_path = Path(metadata["file_path"])
            if file_path.exists():
                # Increment download count
                metadata["download_count"] += 1
                self._save_metadata()  # Persist changes
                return str(file_path)
        return None
    
    def list_files(self) -> List[Dict]:
        """List all active files"""
        # Try to rebuild metadata if we have no files listed
        if not self.file_metadata:
            self._rebuild_metadata_from_files()
            
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
            self._save_metadata()  # Persist changes
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
        # Try to rebuild metadata if we have no files listed
        if not self.file_metadata:
            self._rebuild_metadata_from_files()
            
        total_files = len([m for m in self.file_metadata.values() if m.get("is_active")])
        total_size = sum(m["file_size"] for m in self.file_metadata.values() if m.get("is_active"))
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_dir": str(self.base_dir),
            "metadata_file": str(self.metadata_file)
        }


# Global file storage instance
file_storage = FileStorageService() 