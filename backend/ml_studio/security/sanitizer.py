from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path


class DatasetSanitizer:
    """
    Handles SHA-256 dataset integrity verification and secure file deletion.
    Ensures no residual plaintext data remains after dataset deletion.
    """

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Compute SHA-256 hex digest for a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def compute_sha256_bytes(data: bytes) -> str:
        """Compute SHA-256 hex digest for a byte buffer."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify_integrity(file_path: Path, expected_hash: str) -> bool:
        """
        Verify file integrity by comparing current SHA-256 against expected hash.
        Returns True if hashes match.
        """
        if not file_path.exists():
            return False
        actual_hash = DatasetSanitizer.compute_sha256(file_path)
        return secrets.compare_digest(actual_hash.encode(), expected_hash.encode())

    @staticmethod
    def secure_delete(file_path: Path, passes: int = 3) -> bool:
        """
        Securely shred a file by overwriting with random bytes before deletion.
        Prevents forensic recovery of sensitive training data.

        Args:
            file_path: Path to file to be deleted.
            passes: Number of random overwrite passes (default 3).

        Returns:
            True if file was successfully shredded and deleted.
        """
        if not file_path.exists():
            return False

        try:
            file_size = file_path.stat().st_size
            with open(file_path, "r+b") as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            file_path.unlink()
            return True
        except OSError:
            # Fall back to regular delete if overwrite fails
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False
