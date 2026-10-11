import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings

class TokenEncryptionService:
    """
    AES-256-GCM authenticated encryption service for OAuth tokens and sensitive candidate PII.
    Generates a unique 96-bit (12-byte) initialization vector per encryption.
    """
    def __init__(self, hex_key: str = settings.ENCRYPTION_MASTER_KEY):
        if settings.ENVIRONMENT == "production":
            if not hex_key:
                raise RuntimeError("Production ENCRYPTION_MASTER_KEY must be provided and non-empty.")
            try:
                self.key = bytes.fromhex(hex_key)
                if len(self.key) != 32:
                    raise RuntimeError("Production ENCRYPTION_MASTER_KEY must be exactly 32 bytes (64 hex characters).")
            except Exception as exc:
                raise RuntimeError(f"Failed to parse production ENCRYPTION_MASTER_KEY: {exc}")
        else:
            if hex_key:
                try:
                    self.key = bytes.fromhex(hex_key)
                    if len(self.key) != 32:
                        self.key = self.key.ljust(32, b'\0')[:32]
                except ValueError:
                    # Deterministic test key for local development and test runs
                    import hashlib
                    self.key = hashlib.sha256(b"jobpilot_dev_transient_key_not_for_production").digest()
            else:
                import hashlib
                self.key = hashlib.sha256(b"jobpilot_dev_transient_key_not_for_production").digest()
        self.aesgcm = AESGCM(self.key)


    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts a plaintext string and returns base64-encoded ciphertext with IV prefix.
        """
        if not plaintext:
            return ""
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        # Store as nonce + ciphertext
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, encoded_ciphertext: str) -> str:
        """
        Decrypts a base64-encoded combined ciphertext string.
        """
        if not encoded_ciphertext:
            return ""
        try:
            combined = base64.b64decode(encoded_ciphertext.encode('utf-8'))
            nonce = combined[:12]
            ciphertext = combined[12:]
            decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {str(e)}")

token_encryptor = TokenEncryptionService()
