"""Sozawen License Validation — Stripe-backed.

Keys are SOZA-XXXX-XXXX-XXXX, deterministically derived from Stripe checkout
session IDs on the Sozawen license server. Validation POSTs the key to the
server, which recomputes keys for recent completed sessions and matches.

Honor system is still the policy: check_license() returns valid regardless of
activation status so the app never blocks a musician. Activation tags a user
as "thanks-for-buying" and enables any future paid-only features.
"""

import json
import hashlib
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("sozawen.license")

LICENSE_CACHE = Path.home() / ".sozawen" / "license.json"
LICENSE_SERVER = "https://notare-updates.onrender.com"


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
    """Validate a license key against the Sozawen license server."""
    try:
        import requests
        r = requests.post(
            f"{LICENSE_SERVER}/api/sozawen/validate",
            json={"key": key},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        data = r.json()
        if data.get("valid"):
            _save_cache({
                "key": key,
                "machine_id": _get_machine_id(),
                "valid": True,
                "email": data.get("email"),
                "type": data.get("type", "self_purchase"),
                "purchased_at": data.get("purchased_at"),
            })
            return True, data.get("message") or "License valid!"
        return False, data.get("message") or "Invalid key"
    except ImportError:
        return False, "Network library not available"
    except Exception as e:
        return False, str(e)


def activate_key(key):
    """Activate a license key on this machine."""
    if not key or not isinstance(key, str):
        return False, "No key provided"
    key = key.strip().upper()[:64]
    # Accept SOZA-XXXX-XXXX-XXXX format
    import re as _re
    if not _re.match(r'^SOZA-[A-Z2-7]{4}-[A-Z2-7]{4}-[A-Z2-7]{4}$', key):
        return False, "Invalid key format — expected SOZA-XXXX-XXXX-XXXX"
    return validate_key_online(key)


def _legacy_activate_unused(key):
    """Legacy LemonSqueezy activation — kept only to avoid breaking any
    imports; replaced by the Stripe-backed activate_key above. Never called."""
    try:
        import requests
        r = requests.post(
            "https://api.lemonsqueezy.com/v1/licenses/activate",
            json={
                "license_key": key,
                "instance_name": _get_machine_id(),
            },
            headers={"Accept": "application/json"},
            timeout=15,
        )
        data = r.json()
        valid = data.get("valid", False) or data.get("activated", False)

        if valid:
            _save_cache({
                "key": key,
                "machine_id": _get_machine_id(),
                "valid": True,
                "instance_id": data.get("instance", {}).get("id"),
                "meta": data.get("meta", {}),
            })
            return True, "License activated!"
        else:
            error = data.get("error", "Activation failed")
            # Already activated / limit reached — the key is valid, just used
            # If the key status is "active", accept it on this machine
            key_status = data.get("license_key", {}).get("status", "")
            if key_status == "active" and ("already" in error.lower() or "limit" in error.lower()):
                _save_cache({
                    "key": key,
                    "machine_id": _get_machine_id(),
                    "valid": True,
                    "instance_id": None,
                    "meta": data.get("meta", {}),
                })
                return True, "License activated!"
            return False, error
    except Exception as e:
        return False, str(e)


def check_license():
    """Check if the current machine has a valid license.

    Returns (is_valid, message).

    Honor-system launch (v1.0.0+): the app always reports valid. Sozawen never
    blocks a musician from making music. We ask for payment; we don't enforce
    it technically. If someone buys and activates a key, we record it for
    gratitude and for the eventual Stripe-backed license server — but the
    feature set is identical with or without a key. This matches the shipped
    ethos (no cages, no unneeded hurt) and Reaper's 20-year model.
    """
    cache = _load_cache()

    if cache and cache.get("valid") and cache.get("machine_id") == _get_machine_id():
        return True, "Licensed"

    # No key? Still allow use. Tag it so the UI can show a soft "please consider
    # buying" nudge in Preferences later — but no modal, no block, no nag.
    return True, "Unlicensed (honor system)"


def is_licensed():
    """Quick check — returns True if licensed."""
    valid, _ = check_license()
    return valid


def get_license_key():
    """Get the stored license key, if any."""
    cache = _load_cache()
    return cache.get("key") if cache else None
