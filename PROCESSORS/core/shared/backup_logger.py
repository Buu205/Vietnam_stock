#!/usr/bin/env python3
"""
Backup Logger Module
Quản lý backup và logging cho các script cập nhật dữ liệu trong data_processor
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import pandas as pd

logger = logging.getLogger(__name__)


class BackupLogger:
    """Quản lý backup và logging cho các file dữ liệu."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Khởi tạo BackupLogger.
        
        Args:
            log_dir: Thư mục lưu log backup (mặc định: data_processor/logs/backup)
        """
        if log_dir is None:
            # Default to data_processor/logs/backup
            current_file = Path(__file__)
            log_dir = current_file.parent.parent / "logs" / "backup"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file path
        self.log_file = self.log_dir / f"backup_log_{datetime.now().strftime('%Y%m')}.json"
        
        logger.info(f"BackupLogger initialized. Log directory: {self.log_dir}")
    
    def create_backup(self, 
                     source_file: Path, 
                     backup_suffix: Optional[str] = None,
                     keep_latest_only: bool = True) -> Optional[Path]:
        """
        Tạo backup cho file và log lại.
        
        Args:
            source_file: Đường dẫn file cần backup
            backup_suffix: Hậu tố cho file backup (mặc định: timestamp)
            keep_latest_only: Nếu True, chỉ giữ lại backup mới nhất, xóa các bản cũ
        
        Returns:
            Đường dẫn file backup đã tạo hoặc None nếu lỗi
        """
        try:
            source_file = Path(source_file)
            
            if not source_file.exists():
                logger.warning(f"Source file does not exist: {source_file}")
                return None
            
            # Tạo tên file backup
            if backup_suffix is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_suffix = f"backup_{timestamp}"
            
            # Xác định extension
            if source_file.suffix:
                backup_path = source_file.parent / f"{source_file.stem}_{backup_suffix}{source_file.suffix}"
            else:
                backup_path = source_file.parent / f"{source_file.name}_{backup_suffix}"
            
            # Nếu keep_latest_only, xóa các backup cũ cùng pattern
            if keep_latest_only:
                self._cleanup_old_backups(source_file, backup_path)
            
            # Copy file
            shutil.copy2(source_file, backup_path)
            
            # Lấy thông tin file
            file_size = source_file.stat().st_size
            backup_size = backup_path.stat().st_size
            
            # Log backup
            backup_info = {
                "timestamp": datetime.now().isoformat(),
                "source_file": str(source_file),
                "backup_file": str(backup_path),
                "source_size_bytes": file_size,
                "backup_size_bytes": backup_size,
                "source_size_mb": round(file_size / 1024 / 1024, 2),
                "backup_size_mb": round(backup_size / 1024 / 1024, 2),
                "status": "success"
            }
            
            self._log_backup(backup_info)
            
            logger.info(f"✅ Backup created: {backup_path.name} ({backup_info['backup_size_mb']} MB)")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Error creating backup for {source_file}: {e}")
            backup_info = {
                "timestamp": datetime.now().isoformat(),
                "source_file": str(source_file),
                "backup_file": None,
                "status": "failed",
                "error": str(e)
            }
            self._log_backup(backup_info)
            return None
    
    def _cleanup_old_backups(self, source_file: Path, new_backup: Path) -> None:
        """
        Xóa các file backup cũ cùng pattern, chỉ giữ lại file mới nhất.
        
        Args:
            source_file: File gốc
            new_backup: File backup mới sẽ được tạo
        """
        try:
            # Tìm pattern backup (ví dụ: filename_backup_*.ext)
            source_stem = source_file.stem
            source_ext = source_file.suffix
            
            # Tìm tất cả file backup cùng pattern
            backup_patterns = [
                f"{source_stem}_backup_*{source_ext}",
                f"{source_stem}.backup*",
                f"{source_file.name}.backup*",
            ]
            
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(source_file.parent.glob(pattern))
            
            if not backup_files:
                return
            
            # Loại bỏ file backup mới (chưa tồn tại) khỏi danh sách
            existing_backups = [f for f in backup_files if f.exists() and f != new_backup]
            
            if len(existing_backups) <= 1:
                # Chỉ có 1 hoặc 0 backup, không cần xóa
                return
            
            # Sắp xếp theo thời gian modified (mới nhất trước)
            existing_backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Giữ lại file mới nhất, xóa các file cũ
            latest_backup = existing_backups[0]
            old_backups = existing_backups[1:]
            
            deleted_count = 0
            deleted_size = 0
            
            for old_backup in old_backups:
                try:
                    size = old_backup.stat().st_size
                    old_backup.unlink()
                    deleted_count += 1
                    deleted_size += size
                    logger.info(f"  🗑️  Deleted old backup: {old_backup.name}")
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not delete {old_backup.name}: {e}")
            
            if deleted_count > 0:
                logger.info(f"  ✅ Cleaned up {deleted_count} old backups ({deleted_size / 1024 / 1024:.2f} MB freed)")
                
        except Exception as e:
            logger.warning(f"Error during backup cleanup: {e}")
    
    def _log_backup(self, backup_info: Dict[str, Any]) -> None:
        """
        Ghi log backup vào file JSON.
        
        Args:
            backup_info: Thông tin backup
        """
        try:
            # Load existing logs
            logs = []
            if self.log_file.exists():
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except (json.JSONDecodeError, IOError):
                    logs = []
            
            # Append new log
            logs.append(backup_info)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Write back
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Could not write backup log: {e}")
    
    def get_backup_history(self, source_file: Optional[Path] = None, limit: int = 10) -> list:
        """
        Lấy lịch sử backup.
        
        Args:
            source_file: Lọc theo file gốc (optional)
            limit: Số lượng bản ghi trả về
        
        Returns:
            Danh sách các backup gần nhất
        """
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Filter by source file if provided
            if source_file:
                source_str = str(source_file)
                logs = [log for log in logs if log.get('source_file') == source_str]
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return logs[:limit]
            
        except Exception as e:
            logger.warning(f"Could not read backup history: {e}")
            return []
    
    def list_backups(self, source_file: Path) -> list:
        """
        Liệt kê tất cả file backup của một file gốc.
        
        Args:
            source_file: File gốc
        
        Returns:
            Danh sách các file backup (sắp xếp theo thời gian, mới nhất trước)
        """
        try:
            source_file = Path(source_file)
            source_stem = source_file.stem
            source_ext = source_file.suffix
            
            backup_patterns = [
                f"{source_stem}_backup_*{source_ext}",
                f"{source_stem}.backup*",
                f"{source_file.name}.backup*",
            ]
            
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(source_file.parent.glob(pattern))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return backup_files
            
        except Exception as e:
            logger.warning(f"Error listing backups: {e}")
            return []


# Convenience function for quick backup
def create_backup(source_file: Path, 
                 backup_suffix: Optional[str] = None,
                 keep_latest_only: bool = True,
                 log_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Hàm tiện ích để tạo backup nhanh.
    
    Args:
        source_file: File cần backup
        backup_suffix: Hậu tố backup (mặc định: timestamp)
        keep_latest_only: Chỉ giữ backup mới nhất
        log_dir: Thư mục log (mặc định: data_processor/logs/backup)
    
    Returns:
        Đường dẫn file backup hoặc None
    """
    backup_logger = BackupLogger(log_dir=log_dir)
    return backup_logger.create_backup(source_file, backup_suffix, keep_latest_only)

