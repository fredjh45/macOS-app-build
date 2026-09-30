"""
License Guard & Anti-Tamper Enforcement Engine.
Handles local persistent activation, machine node-locking, and self-corruption on tamper.
"""

import os
import sys
import json
import logging
from typing import Tuple, Dict, Any, Optional

from core.security.hwid import get_hardware_fingerprint
from core.security.crypto_util import (
    verify_license_matches_hwid,
    encrypt_local_license,
    decrypt_local_license
)
from core.security.supabase_client import (
    verify_license_with_supabase,
    report_tamper_alert
)
from database.db import get_setting, set_setting, DB_PATH

from core.path_helper import get_license_file_path
LICENSE_FILE_PATH = get_license_file_path()

class LicenseGuard:
    _cached_status: Optional[bool] = None

    @classmethod
    def get_hwid(cls) -> str:
        return get_hardware_fingerprint()

    @classmethod
    def self_destruct(cls, reason: str, license_key: str = ""):
        """
        Actively corrupts local session storage and permanently blacklists the license key on Supabase.
        Triggered when unauthorized decryption, binary tampering, or invalid HWID is detected.
        """
        logger.critical(f"[SECURITY] SELF-CORRUPTION TRIGGERED: {reason}")
        
        # 1. Report tamper alert to Supabase
        hwid = cls.get_hwid()
        saved_key = license_key or get_setting("license_key", "")
        if saved_key:
            report_tamper_alert(saved_key, hwid, reason=reason)
            
        # 2. Corrupt local license storage file
        if os.path.exists(LICENSE_FILE_PATH):
            try:
                with open(LICENSE_FILE_PATH, "wb") as f:
                    f.write(b"\x00" * 512)  # Zero-fill
                os.remove(LICENSE_FILE_PATH)
            except Exception:
                pass

        # 3. Corrupt local database file with null bytes
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "wb") as f:
                    f.write(b"\x00" * 4096)  # Overwrite SQLite header with null bytes
            except Exception:
                pass

        # 4. Immediate hard process exit without traceback
        os._exit(1)

    @classmethod
    def check_local_activation(cls) -> Tuple[bool, str]:
        """
        Fast startup check. Reads locally saved encrypted license.
        If file was transferred to another PC or modified, it will fail decryption.
        """
        hwid = cls.get_hwid()

        # Check in local encrypted file
        encrypted_token = None
        if os.path.exists(LICENSE_FILE_PATH):
            try:
                with open(LICENSE_FILE_PATH, "r", encoding="ascii") as f:
                    encrypted_token = f.read().strip()
            except Exception:
                pass

        # Fallback to database setting
        if not encrypted_token:
            encrypted_token = get_setting("encrypted_license_token", "").strip()

        if not encrypted_token:
            return False, "Application is not activated."

        # Attempt decryption using current machine's HWID
        license_data = decrypt_local_license(encrypted_token, hwid)
        if not license_data:
            # Tamper detected or file copied to another machine with different HWID!
            cls.self_destruct("License file decrypted with invalid HWID or checksum failed.")
            return False, "Integrity check failed."

        saved_key = license_data.get("license_key", "")
        saved_hwid = license_data.get("hardware_id", "")

        # Verify mathematical HMAC signature binding
        if not verify_license_matches_hwid(saved_key, hwid) or saved_hwid != hwid:
            cls.self_destruct("Cryptographic signature mismatch with current hardware.", license_key=saved_key)
            return False, "Hardware signature mismatch."

        # Online verification check with Supabase (Fast check with 4s timeout)
        is_valid, msg, record = verify_license_with_supabase(saved_key, hwid, timeout=4)
        if not is_valid:
            if "reach license server" in msg.lower():
                # Allow offline execution if locally cryptographically valid
                logger.info("[LICENSE] Offline mode: Local cryptographic signature verified.")
                return True, "Active (Offline Mode)"
            elif "tamper" in msg.lower() or "revoked" in msg.lower():
                cls.self_destruct(f"Revocation/Tamper on server: {msg}", license_key=saved_key)
                return False, msg
            else:
                return False, msg

        return True, "Active"

    @classmethod
    def activate(cls, license_key: str) -> Tuple[bool, str]:
        """
        Activates the license key on this machine and stores it persistently.
        """
        key_clean = license_key.strip().upper()
        hwid = cls.get_hwid()

        if not key_clean.startswith("GSITE-") or len(key_clean) != 25:
            return False, "Invalid License Key format. Example: GSITE-XXXX-XXXX-XXXX-XXXX"

        # 1. Cryptographic mathematical check (Is key signed for this HWID?)
        if not verify_license_matches_hwid(key_clean, hwid):
            return False, "This License Key is NOT generated for this machine's Hardware ID!"

        # 2. Online verification with Supabase
        is_valid, msg, record = verify_license_with_supabase(key_clean, hwid)
        if not is_valid:
            return False, f"Server rejected key: {msg}"

        # 3. Encrypt and persist locally for permanent single-click launches
        payload = {
            "license_key": key_clean,
            "hardware_id": hwid,
            "client_name": record.get("client_name", "Client") if record else "Client"
        }
        encrypted_token = encrypt_local_license(payload, hwid)

        # Save to database
        set_setting("encrypted_license_token", encrypted_token)
        set_setting("license_key", key_clean)

        # Save to hidden local file
        try:
            os.makedirs(os.path.dirname(LICENSE_FILE_PATH), exist_ok=True)
            with open(LICENSE_FILE_PATH, "w", encoding="ascii") as f:
                f.write(encrypted_token)
        except Exception as e:
            logger.warning(f"[LICENSE] Could not write hidden file: {e}")

        logger.info(f"[LICENSE] License {key_clean} activated successfully and saved permanently.")
        return True, "License successfully activated!"
