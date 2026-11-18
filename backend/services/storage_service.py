"""
backend/services/storage_service.py
=====================================
Storage abstraction layer — supports two modes:

    LOCAL mode  (STORAGE_MODE=local)
    ─────────────────────────────────
    Files are read/written to the local data/ directory.
    Directory structure mirrors the HDFS layout so the code
    is identical regardless of mode.

    HDFS mode   (STORAGE_MODE=hdfs)
    ─────────────────────────────────
    Files are read/written via WebHDFS REST API using the
    'hdfs' Python library.  Requires a running Hadoop cluster.

BDT Concept:
    HDFS (Hadoop Distributed File System) stores files across
    multiple DataNodes, with a NameNode tracking the directory
    tree.  The local mode mirrors this layout so students can
    understand the structure before connecting a real cluster.

Directory architecture (same in local and HDFS):
    <base>/raw/shipments/
    <base>/raw/traffic/
    <base>/raw/weather/
    <base>/raw/gps/
    <base>/processed/
    <base>/analytics/
    <base>/models/
"""

import shutil
from pathlib import Path
from datetime import datetime, timezone
from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    Unified file I/O service.
    Instantiate once; call save_file(), read_file(), list_files(), etc.
    The caller never needs to know whether storage is local or HDFS.
    """

    def __init__(self):
        self.mode = Config.STORAGE_MODE
        if self.mode == "hdfs":
            self._init_hdfs()
        else:
            self._init_local()
        logger.info("StorageService initialised in '%s' mode", self.mode)

    # ── Initialisation ─────────────────────────────────────

    def _init_local(self):
        """Ensure all local subdirectories exist."""
        self.base = Config.DATA_DIR
        subdirs = [
            "raw/shipments", "raw/traffic", "raw/weather", "raw/gps",
            "processed", "analytics", "models", "sample",
        ]
        for sub in subdirs:
            (self.base / sub).mkdir(parents=True, exist_ok=True)

    def _init_hdfs(self):
        """
        Initialise HDFS client.
        Requires the 'hdfs' package: pip install hdfs
        and a running Hadoop cluster (NameNode accessible).
        """
        try:
            from hdfs import InsecureClient
            url = f"http://{Config.HDFS_HOST}:50070"  # WebHDFS port
            self.hdfs_client = InsecureClient(url, user=Config.HDFS_USER)
            self.base = Config.HDFS_BASE_PATH
            logger.info("HDFS client connected to %s", url)
        except ImportError:
            logger.error(
                "hdfs package not installed. Run: pip install hdfs\n"
                "Falling back to local mode."
            )
            self.mode = "local"
            self._init_local()
        except Exception as exc:
            logger.error("HDFS connection failed: %s. Falling back to local.", exc)
            self.mode = "local"
            self._init_local()

    # ── Public API ─────────────────────────────────────────

    def save_file(
        self,
        source_path: str | Path,
        dataset_type: str,
        filename: str | None = None,
    ) -> str:
        """
        Copy a file into the appropriate raw/<dataset_type>/ directory.

        Args:
            source_path:  Path to the uploaded/temp file on disk.
            dataset_type: 'shipments' | 'traffic' | 'weather' | 'gps'
            filename:     Override destination filename (optional).

        Returns:
            The destination path string (local path or HDFS path).
        """
        source_path = Path(source_path)
        if filename is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{ts}_{source_path.name}"

        dest_subdir = f"raw/{dataset_type}"

        if self.mode == "local":
            return self._save_local(source_path, dest_subdir, filename)
        else:
            return self._save_hdfs(source_path, dest_subdir, filename)

    def read_file(self, relative_path: str) -> Path | None:
        """
        Return a local Path object for the given relative storage path.
        For HDFS mode, downloads the file to a temp location first.

        Args:
            relative_path: e.g. 'raw/shipments/my_file.csv'

        Returns:
            Local Path object to read from, or None if not found.
        """
        if self.mode == "local":
            full = self.base / relative_path
            return full if full.exists() else None
        else:
            return self._download_from_hdfs(relative_path)

    def list_files(self, subdir: str = "") -> list[dict]:
        """
        List files in a storage subdirectory.

        Args:
            subdir: e.g. 'raw/shipments'

        Returns:
            List of dicts: [{name, path, size_kb, modified}]
        """
        if self.mode == "local":
            return self._list_local(subdir)
        else:
            return self._list_hdfs(subdir)

    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists in storage."""
        if self.mode == "local":
            return (self.base / relative_path).exists()
        else:
            try:
                self.hdfs_client.status(
                    f"{self.base}/{relative_path}", strict=False
                )
                return True
            except Exception:
                return False

    def get_storage_info(self) -> dict:
        """Return storage configuration summary for the health endpoint."""
        if self.mode == "local":
            total = sum(
                f.stat().st_size
                for f in self.base.rglob("*")
                if f.is_file()
            )
            return {
                "mode": "local",
                "base_path": str(self.base),
                "total_size_mb": round(total / (1024 * 1024), 2),
                "note": "Local filesystem — mirrors HDFS directory layout",
            }
        else:
            return {
                "mode": "hdfs",
                "namenode": f"{Config.HDFS_HOST}:{Config.HDFS_PORT}",
                "base_path": self.base,
                "note": "Apache HDFS distributed storage",
            }

    # ── Local helpers ──────────────────────────────────────

    def _save_local(self, source: Path, subdir: str, filename: str) -> str:
        dest_dir = self.base / subdir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        shutil.copy2(source, dest)
        logger.info("Saved to local storage: %s", dest)
        return str(dest)

    def _list_local(self, subdir: str) -> list[dict]:
        target = self.base / subdir if subdir else self.base
        if not target.exists():
            return []
        result = []
        for f in sorted(target.iterdir()):
            if f.is_file():
                stat = f.stat()
                result.append({
                    "name":        f.name,
                    "path":        str(f.relative_to(self.base)),
                    "size_kb":     round(stat.st_size / 1024, 1),
                    "modified":    datetime.fromtimestamp(
                                       stat.st_mtime, tz=timezone.utc
                                   ).isoformat(),
                })
        return result

    # ── HDFS helpers ───────────────────────────────────────

    def _save_hdfs(self, source: Path, subdir: str, filename: str) -> str:
        hdfs_path = f"{self.base}/{subdir}/{filename}"
        try:
            with open(source, "rb") as f:
                self.hdfs_client.write(hdfs_path, f, overwrite=True)
            logger.info("Saved to HDFS: %s", hdfs_path)
            return hdfs_path
        except Exception as exc:
            logger.error("HDFS write failed: %s", exc)
            raise

    def _download_from_hdfs(self, relative_path: str) -> Path | None:
        import tempfile
        hdfs_path = f"{self.base}/{relative_path}"
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(relative_path).suffix
            )
            with self.hdfs_client.read(hdfs_path) as reader:
                tmp.write(reader.read())
            tmp.close()
            return Path(tmp.name)
        except Exception as exc:
            logger.error("HDFS read failed for %s: %s", hdfs_path, exc)
            return None

    def _list_hdfs(self, subdir: str) -> list[dict]:
        hdfs_path = f"{self.base}/{subdir}" if subdir else self.base
        try:
            files = self.hdfs_client.list(hdfs_path, status=True)
            return [
                {
                    "name":     name,
                    "path":     f"{subdir}/{name}",
                    "size_kb":  round(info["length"] / 1024, 1),
                    "modified": datetime.fromtimestamp(
                                    info["modificationTime"] / 1000, tz=timezone.utc
                                ).isoformat(),
                }
                for name, info in files
                if info["type"] == "FILE"
            ]
        except Exception as exc:
            logger.error("HDFS list failed for %s: %s", hdfs_path, exc)
            return []


# Module-level singleton (import and use directly)
storage = StorageService()

