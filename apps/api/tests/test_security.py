import pytest
from app.core.security import TokenEncryptionService

def test_aes_encryption_roundtrip():
    service = TokenEncryptionService("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    token = "ya29.a0AfH6SMD_sample_google_oauth_refresh_token_123456789"
    
    # Encrypt
    encrypted = service.encrypt(token)
    assert encrypted != token
    assert len(encrypted) > 20
    
    # Decrypt
    decrypted = service.decrypt(encrypted)
    assert decrypted == token

def test_empty_token_encryption():
    service = TokenEncryptionService()
    assert service.encrypt("") == ""
    assert service.decrypt("") == ""

def test_corrupted_ciphertext_fails_gracefully():
    service = TokenEncryptionService()
    with pytest.raises(ValueError):
        service.decrypt("invalid_base64_ciphertext_that_should_fail")
