"""Sozawen License Validation — LemonSqueezy integration.

Validates license keys against LemonSqueezy API.
Caches validation locally with hardware fingerprint for offline use.
"""

import json
import hashlib
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("sozawen.license")

LICENSE_CACHE = Path.home() / ".sozawen" / "license.json"
STORE_ID = "sozawen"  # LemonSqueezy store slug


def _get_machine_id():
    """Get a stable hardware fingerprint (Windows MachineGuid)."""
    try:
        result = subprocess.run(
            ['reg', 'query', r'HKLM\SOFTWARE\Microsoft\Cryptography', '/v', 'MachineGuid'],
            capture_output=True, text=True, timeout=5,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        for line in result.stdout.split('\n'):
            if 'MachineGuid' in line:
                return line.strip().split()[-1]
    except Exception:
        pass
    # Fallback: hash of computer name + username
    import os
    return hashlib.sha256(f"{os.environ.get('COMPUTERNAME','')}{os.environ.get('USERNAME','')}".encode()).hexdigest()[:36]


def _load_cache():
    """Load cached license validation."""
    try:
        if LICENSE_CACHE.exists():
            return json.loads(LICENSE_CACHE.read_text())
    except Exception:
        pass
    return None


def _save_cache(data):
    """Save license validation to cache."""
    try:
        LICENSE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        LICENSE_CACHE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        logger.warning("Could not save license cache: %s", e)


def validate_key_online(key):
    """Validate a license key against LemonSqueezy API."""
    try:
        import requests
        r = requests.post(
            "https://api.lemonsqueezy.com/v1/licenses/validate",
            json={"license_key": key, "instance_name": _get_machine_id()},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            valid = data.get("valid", False)
            if valid:
                _save_cache({
                    "key": key,
                    "machine_id": _get_machine_id(),
                    "valid": True,
                    "meta": data.get("meta", {}),
                })
                return True, "License activated!"
            else:
                error = data.get("error", "Invalid key")
                return False, error
        else:
            return False, f"Server error ({r.status_code})"
    except ImportError:
        return False, "Network library not available"
    except Exception as e:
        return False, str(e)


def activate_key(key):
    """Activate a license key on this machine."""
    try:
        import requests
        r = requests.post(
            "https://api.lemonsqueezy.com/v1/licenses/activate",
            json={
                "license_key": key,
                "instance_name": _get_machine_id(),
            },
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("activated") or data.get("valid"):
                _save_cache({
                    "key": key,
                    "machine_id": _get_machine_id(),
                    "valid": True,
                    "instance_id": data.get("instance", {}).get("id"),
                    "meta": data.get("meta", {}),
                })
                return True, "License activated on this machine!"
            return False, data.get("error", "Activation failed")
        return False, f"Server error ({r.status_code})"
    except Exception as e:
        return False, str(e)


def check_license():
    """Check if the current machine has a valid license.

    Returns (is_valid, message).
    Checks cache first, then validates online if cache is stale.
    """
    cache = _load_cache()

    if cache and cache.get("valid"):
        # Check machine ID matches
        if cache.get("machine_id") == _get_machine_id():
            return True, "Licensed"
        else:
            return False, "License is for a different machine"

    return False, "No license found"


def is_licensed():
    """Quick check — returns True if licensed."""
    valid, _ = check_license()
    return valid


def get_license_key():
    """Get the stored license key, if any."""
    cache = _load_cache()
    return cache.get("key") if cache else None
