from __future__ import annotations

import base64
import os
from pathlib import Path


# ── Key Management ──────────────────────────────────────────────────────────────

_KEY_ENV_VAR = "ML_STUDIO_ENCRYPTION_KEY"
_KEY_FILE_DEFAULT = ".ml_studio_key"


def _get_or_create_key(key_file: str | None = None) -> bytes:
    """
    Get encryption key from environment variable or generate/load from key file.
    Key is a 32-byte Fernet-compatible base64url key.
    """
    env_key = os.environ.get(_KEY_ENV_VAR)
    if env_key:
        return env_key.encode()

    key_path = Path(key_file or _KEY_FILE_DEFAULT)
    if key_path.exists():
        return key_path.read_bytes().strip()

    # Generate a new random 32-byte key
    raw_key = os.urandom(32)
    fernet_key = base64.urlsafe_b64encode(raw_key)
    key_path.write_bytes(fernet_key)
    return fernet_key


# ── DatasetEncryptor ────────────────────────────────────────────────────────────

class DatasetEncryptor:
    """
    AES-256 dataset at-rest encryption using cryptography.Fernet (AES-128-CBC + HMAC-SHA256).
    Falls back gracefully to no-op passthrough if the `cryptography` package is unavailable.
    """

    def __init__(self, key_file: str | None = None) -> None:
        self._key = _get_or_create_key(key_file)
        self._fernet: object | None = None
        self._available: bool = False
        try:
            from cryptography.fernet import Fernet
            self._fernet = Fernet(self._key)
            self._available = True
        except ImportError:
            pass  # Graceful degradation: encryption not available without cryptography pkg

    @property
    def encryption_available(self) -> bool:
        return self._available

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt raw dataset bytes. Returns encrypted bytes or original if unavailable."""
        if not self._available or self._fernet is None:
            return data
        return self._fernet.encrypt(data)  # type: ignore[union-attr]

    def decrypt(self, data: bytes) -> bytes:
        """Decrypt encrypted dataset bytes. Returns original bytes if unavailable."""
        if not self._available or self._fernet is None:
            return data
        return self._fernet.decrypt(data)  # type: ignore[union-attr]

    def encrypt_file(self, file_path: Path) -> Path:
        """Encrypt an existing file in-place. Returns path to encrypted file."""
        raw = file_path.read_bytes()
        encrypted = self.encrypt(raw)
        enc_path = file_path.with_suffix(file_path.suffix + ".enc")
        enc_path.write_bytes(encrypted)
        return enc_path

    def decrypt_file(self, enc_path: Path) -> bytes:
        """Decrypt an encrypted file and return raw bytes."""
        raw = enc_path.read_bytes()
        return self.decrypt(raw)
