"""
FMD2 Python - Crypto Module
Implements cryptographic functions matching Pascal SynaCrypt and OpenSSL bindings
"""

import base64
import hashlib
import hmac
from typing import Optional, Union

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography library not installed. Run: pip install cryptography")
    import sys
    sys.exit(1)


class FMDCrypto:
    """
    Crypto module providing functions compatible with FMD2 Pascal crypto
    """
    
    # Base64 encoding/decoding
    
    def base64_encode(self, data: Union[str, bytes]) -> str:
        """Base64 encode data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('ascii')
    
    def base64_decode(self, data: Union[str, bytes]) -> bytes:
        """Base64 decode data"""
        if isinstance(data, str):
            data = data.encode('ascii')
        return base64.b64decode(data)
    
    # Hash functions
    
    def md5(self, data: Union[str, bytes]) -> str:
        """Calculate MD5 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    def sha1(self, data: Union[str, bytes]) -> str:
        """Calculate SHA1 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha1(data).hexdigest()
    
    def sha256(self, data: Union[str, bytes]) -> str:
        """Calculate SHA256 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def sha512(self, data: Union[str, bytes]) -> str:
        """Calculate SHA512 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()
    
    # HMAC functions
    
    def hmac_sha256(self, data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """Calculate HMAC-SHA256"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        return hmac.new(key, data, hashlib.sha256).hexdigest()
    
    def hmac_sha512(self, data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """Calculate HMAC-SHA512"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        return hmac.new(key, data, hashlib.sha512).hexdigest()
    
    # AES encryption/decryption
    
    def aes_cbc_encrypt(self, data: Union[str, bytes], key: bytes, iv: bytes) -> bytes:
        """AES-CBC encryption"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted
    
    def aes_cbc_decrypt(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """AES-CBC decryption"""
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(data) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        unpadded = unpadder.update(decrypted) + unpadder.finalize()
        
        return unpadded
    
    def aes_ecb_encrypt(self, data: Union[str, bytes], key: bytes) -> bytes:
        """AES-ECB encryption"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted
    
    def aes_ecb_decrypt(self, data: bytes, key: bytes) -> bytes:
        """AES-ECB decryption"""
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(data) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        unpadded = unpadder.update(decrypted) + unpadder.finalize()
        
        return unpadded
    
    # XOR cipher
    
    def xor_cipher(self, data: Union[str, bytes], key: Union[str, bytes]) -> bytes:
        """XOR cipher with repeating key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        result = bytearray(len(data))
        key_len = len(key)
        
        for i in range(len(data)):
            result[i] = data[i] ^ key[i % key_len]
        
        return bytes(result)
    
    # Utility functions
    
    def random_bytes(self, length: int) -> bytes:
        """Generate random bytes"""
        import os
        return os.urandom(length)
    
    def pbkdf2(self, password: str, salt: bytes, iterations: int = 10000, 
               key_length: int = 32, hash_name: str = 'sha256') -> bytes:
        """PBKDF2 key derivation"""
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        kdf = PBKDF2HMAC(
            algorithm=getattr(hashlib, hash_name)(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode('utf-8'))


# Singleton instance
_crypto_instance = None


def get_crypto() -> FMDCrypto:
    """Get singleton crypto instance"""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = FMDCrypto()
    return _crypto_instance
