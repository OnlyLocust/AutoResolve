import hmac
import hashlib
from fastapi import HTTPException

def verify_signature(payload_body: bytes, secret_token: str, signature_header: str):
    if not signature_header:
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 header missing")
    
    # Calculate the expected HMAC signature
    hash_object = hmac.new(
        secret_token.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    # Use compare_digest to prevent timing attacks
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=401, detail="Invalid signature")