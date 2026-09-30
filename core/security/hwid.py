"""
Hardware Identification (HWID) Engine for Windows.
Combines multiple physical hardware components into a cryptographically hashed,
node-locked fingerprint that cannot be spoofed across machines.
"""

import os
import sys
import hashlib
import subprocess
from typing import Dict, Any

if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

HWID_SALT = "GSITE_POSTER_HARDWARE_NODE_LOCK_SALT_2026_SECURE"
_CACHED_HWID = None

def _run_cmd(cmd: list) -> str:
    """Helper to run system commands and return stripped stdout."""
    try:
        kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": 8
        }
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        res = subprocess.run(cmd, **kwargs)
        return res.stdout.strip()
    except Exception:
        return ""

def get_machine_guid() -> str:
    """Retrieves Windows OS MachineGuid from Registry."""
    if not winreg:
        return "REG_GENERIC_GUID"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return str(guid).strip()
    except Exception:
        return "REG_GENERIC_GUID"

def get_mac_hardware_fingerprint() -> str:
    """Retrieves unique hardware UUID and serial number on macOS."""
    uuid = ""
    serial = ""
    # 1. IOPlatformExpertDevice via ioreg
    out = _run_cmd(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"])
    for line in out.splitlines():
        if "IOPlatformUUID" in line:
            parts = line.split("=")
            if len(parts) > 1:
                uuid = parts[1].strip().strip('"')
        elif "IOPlatformSerialNumber" in line:
            parts = line.split("=")
            if len(parts) > 1:
                serial = parts[1].strip().strip('"')
    
    # 2. Fallback to sysctl if ioreg didn't yield UUID
    if not uuid:
        uuid = _run_cmd(["sysctl", "-n", "kern.uuid"])
    
    # 3. Fallback to system_profiler
    if not serial or not uuid:
        sp_out = _run_cmd(["system_profiler", "SPHardwareDataType"])
        for line in sp_out.splitlines():
            if "Serial Number" in line and not serial:
                serial = line.split(":")[-1].strip()
            elif "Hardware UUID" in line and not uuid:
                uuid = line.split(":")[-1].strip()

    raw_signature = f"{uuid}|{serial}|{HWID_SALT}"
    sha = hashlib.sha256(raw_signature.encode('utf-8')).hexdigest().upper()
    return f"HWID-{sha[0:4]}-{sha[4:8]}-{sha[8:12]}-{sha[12:16]}"

def get_hardware_fingerprint() -> str:
    """
    Computes a unique, consistent Hardware ID (HWID) for this machine.
    Uses in-memory caching for instantaneous sub-millisecond retrieval.
    Format: HWID-XXXX-XXXX-XXXX-XXXX
    """
    global _CACHED_HWID
    if _CACHED_HWID:
        return _CACHED_HWID

    if sys.platform == "darwin":
        _CACHED_HWID = get_mac_hardware_fingerprint()
        return _CACHED_HWID

    mb = "MB_GENERIC_SERIAL"
    cpu = "CPU_GENERIC_ID"
    bios = "BIOS_GENERIC_UUID"
    disk = "DISK_GENERIC_SERIAL"

    # Fast combined CIM query via single PowerShell call (drastically cuts startup lag)
    fast_ps_cmd = [
        "powershell", "-NoProfile", "-Command",
        "Write-Output (Get-CimInstance Win32_BaseBoard).SerialNumber; "
        "Write-Output (Get-CimInstance Win32_Processor).ProcessorId; "
        "Write-Output (Get-CimInstance Win32_ComputerSystemProduct).UUID; "
        "Write-Output (Get-CimInstance Win32_DiskDrive | Select-Object -First 1).SerialNumber"
    ]
    raw_out = _run_cmd(fast_ps_cmd)
    lines = [l.strip() for l in raw_out.splitlines() if l.strip()]

    if len(lines) >= 4:
        if lines[0] and lines[0].lower() not in ["none", "default string", ""]:
            mb = lines[0]
        if lines[1] and lines[1].lower() not in ["none", ""]:
            cpu = lines[1]
        if lines[2] and lines[2].lower() not in ["none", ""]:
            bios = lines[2]
        if lines[3] and lines[3].lower() not in ["none", ""]:
            disk = lines[3]
    else:
        # Fallback to individual WMIC if CIM fails
        try:
            wmic_mb = _run_cmd(["wmic", "baseboard", "get", "serialnumber"]).splitlines()
            for l in wmic_mb:
                if l.strip() and "serialnumber" not in l.lower():
                    mb = l.strip()
                    break
            wmic_cpu = _run_cmd(["wmic", "cpu", "get", "processorid"]).splitlines()
            for l in wmic_cpu:
                if l.strip() and "processorid" not in l.lower():
                    cpu = l.strip()
                    break
        except Exception:
            pass

    guid = get_machine_guid()

    raw_signature = f"{mb}|{cpu}|{bios}|{disk}|{guid}|{HWID_SALT}"
    sha = hashlib.sha256(raw_signature.encode('utf-8')).hexdigest().upper()

    part1 = sha[0:4]
    part2 = sha[4:8]
    part3 = sha[8:12]
    part4 = sha[12:16]

    _CACHED_HWID = f"HWID-{part1}-{part2}-{part3}-{part4}"
    return _CACHED_HWID

if __name__ == "__main__":
    print("Machine Hardware ID:", get_hardware_fingerprint())
