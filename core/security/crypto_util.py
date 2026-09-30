"""
Cryptographic Utilities for License Key Generation, Signatures, and Local Vault Encryption.
"""

import hmac
import hashlib
import base64
import json
import os
from typing import Optional, Dict, Any

# Internal Master Secret Salt (Used for mathematical HWID-binding)
MASTER_LICENSE_SECRET = b"GSITE_POSTER_MASTER_CRYPT_2026_x89aF!@#_ANTIGRAVITY"

def generate_license_key(hwid: str, client_name: str = "Client") -> str:
    """
    Generates a deterministic, cryptographically signed license key strictly bound to this HWID.
    Format: GSITE-XXXX-XXXX-XXXX-XXXX (24 characters)
    """
    hwid_clean = hwid.strip().upper()
    payload = f"{hwid_clean}|{MASTER_LICENSE_SECRET.decode('latin1')}".encode('utf-8')
    
    # Compute HMAC-SHA256
    sig = hmac.new(MASTER_LICENSE_SECRET, payload, hashlib.sha256).hexdigest().upper()
    
    part1 = sig[0:4]
    part2 = sig[4:8]
    part3 = sig[8:12]
    part4 = sig[12:16]
    
    return f"GSITE-{part1}-{part2}-{part3}-{part4}"

def verify_license_matches_hwid(license_key: str, hwid: str) -> bool:
    """
    Cryptographically verifies whether a given License Key was generated for this specific HWID.
    Prevents running the same key on a different machine even without an internet connection!
    """
    if not license_key or not hwid:
        return False
    
    key_clean = license_key.strip().upper()
    expected_key = generate_license_key(hwid)
    return hmac.compare_digest(key_clean, expected_key)

def encrypt_local_license(license_data: Dict[str, Any], hwid: str) -> str:
    """
    Encrypts local license payload using a key derived from the local machine's HWID.
    If the encrypted file is copied to another PC, that PC's different HWID will fail to decrypt it!
    """
    raw_json = json.dumps(license_data).encode('utf-8')
    # Derive 32-byte key from HWID
    derived_key = hashlib.sha256(f"{hwid}|{MASTER_LICENSE_SECRET.decode('latin1')}".encode('utf-8')).digest()
    
    # Simple, high-speed XOR stream cipher with derived key hash
    encrypted = bytearray()
    key_len = len(derived_key)
    for i, b in enumerate(raw_json):
        encrypted.append(b ^ derived_key[i % key_len])
    
    # Prepend checksum to verify integrity
    checksum = hashlib.sha256(raw_json).digest()[:8]
    payload = checksum + bytes(encrypted)
    return base64.b64encode(payload).decode('ascii')

def decrypt_local_license(encrypted_str: str, hwid: str) -> Optional[Dict[str, Any]]:
    """
    Decrypts local license payload. Returns None if decryption or checksum fails (tampered or wrong PC).
    """
    try:
        payload = base64.b64decode(encrypted_str.encode('ascii'))
        if len(payload) <= 8:
            return None
        
        stored_checksum = payload[:8]
        encrypted_bytes = payload[8:]
        
        derived_key = hashlib.sha256(f"{hwid}|{MASTER_LICENSE_SECRET.decode('latin1')}".encode('utf-8')).digest()
        key_len = len(derived_key)
        
        decrypted = bytearray()
        for i, b in enumerate(encrypted_bytes):
            decrypted.append(b ^ derived_key[i % key_len])
        
        raw_json = bytes(decrypted)
        calc_checksum = hashlib.sha256(raw_json).digest()[:8]
        
        if not hmac.compare_digest(stored_checksum, calc_checksum):
            # Checksum failed! Tampered or transferred to another PC!
            return None
        
        return json.loads(raw_json.decode('utf-8'))
    except Exception:
        return None
