"""
Supabase REST API Client for License Verification, Activation, and Tamper Alerts.
"""

import requests
import json
import logging
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

SUPABASE_URL = "https://xbuczlcphoujyniewuxi.supabase.co"
SUPABASE_KEY = "sb_publishable_-FcLuVS38nf90EKR8-dOWA_H7KzbU4i"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def verify_license_with_supabase(license_key: str, hwid: str, timeout: int = 5) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Queries Supabase to verify if the license exists, matches this HWID, and is ACTIVE.
    Returns: (is_valid, message, license_record)
    """
    key_clean = license_key.strip().upper()
    hwid_clean = hwid.strip().upper()
    
    url = f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{key_clean}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200:
            return False, f"Server communication error ({r.status_code})", None
        
        rows = r.json()
        if not rows or len(rows) == 0:
            return False, "Invalid License Key. No matching record found.", None
        
        record = rows[0]
        rec_hwid = str(record.get("hardware_id", "")).strip().upper()
        status = str(record.get("status", "")).strip().upper()
        tamper = record.get("tamper_detected", False)
        expires_at = record.get("expires_at")
        
        # Check HWID Match (Node Lock)
        if rec_hwid != hwid_clean:
            # Check if record has no HWID bound yet (unbound key)
            if not rec_hwid or rec_hwid == "NULL" or rec_hwid == "":
                # First time activation on this machine
                pass
            else:
                return False, "This License Key is locked to a different computer!", record
        
        # Check Tamper Flag
        if tamper:
            return False, "This License has been revoked due to integrity violation/tampering!", record
        
        # Check Status
        if status != "ACTIVE":
            return False, f"License is not active (Status: {status})", record
        
        # Check Expiration
        if expires_at:
            try:
                # ISO parsing
                exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > exp_dt:
                    return False, f"License expired on {exp_dt.strftime('%Y-%m-%d')}", record
            except Exception:
                pass
        
        # Update last verified timestamp silently
        update_url = f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{key_clean}"
        now_iso = datetime.now(timezone.utc).isoformat()
        update_payload = {"last_verified_at": now_iso}
        if not rec_hwid:
            # Bind HWID and activated_at on first activation
            update_payload["hardware_id"] = hwid_clean
            update_payload["activated_at"] = now_iso
            
        requests.patch(update_url, headers=HEADERS, json=update_payload, timeout=3)
        
        return True, "License is valid and active.", record
    except requests.exceptions.RequestException as e:
        logger.warning(f"[SUPABASE] Network check failed: {e}")
        return False, "Unable to reach license server. Check your internet connection.", None
    except Exception as e:
        logger.exception(f"[SUPABASE] Error during license verification: {e}")
        return False, f"Verification error: {str(e)}", None

def report_tamper_alert(license_key: str, hwid: str, reason: str = "Integrity check failed"):
    """
    Reports unauthorized modification or crack attempt to Supabase to permanently blacklist the key.
    """
    key_clean = license_key.strip().upper()
    url = f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{key_clean}"
    try:
        payload = {
            "status": "TAMPERED",
            "tamper_detected": True,
            "last_verified_at": datetime.now(timezone.utc).isoformat()
        }
        requests.patch(url, headers=HEADERS, json=payload, timeout=5)
        logger.critical(f"[SECURITY] Tamper alert sent to Supabase for key {key_clean} ({reason})")
    except Exception:
        pass

def insert_license_record(license_key: str, hardware_id: str, client_name: str = "Client", expires_at: Optional[str] = None) -> Tuple[bool, str]:
    """
    Used by Keygen to add a new license record to Supabase.
    """
    url = f"{SUPABASE_URL}/rest/v1/licenses"
    payload = {
        "license_key": license_key.strip().upper(),
        "hardware_id": hardware_id.strip().upper(),
        "client_name": client_name.strip() or "Client",
        "status": "ACTIVE",
        "tamper_detected": False,
        "expires_at": expires_at
    }
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=8)
        if r.status_code in [200, 201]:
            return True, "License successfully added to Supabase."
        elif r.status_code == 409 or "duplicate" in r.text.lower():
            return False, "A license for this key or hardware ID already exists in Supabase."
        else:
            return False, f"Failed to insert into Supabase ({r.status_code}): {r.text}"
    except Exception as e:
        return False, f"Network error connecting to Supabase: {str(e)}"
