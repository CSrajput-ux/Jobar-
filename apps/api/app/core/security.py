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
        try:
            self.key = bytes.fromhex(hex_key)
            if len(self.key) != 32:
                # Fallback to padded key if non-32 byte provided in development
                self.key = self.key.ljust(32, b'\0')[:32]
        except ValueError:
            self.key = b"01234567890123456789012345678901"
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
