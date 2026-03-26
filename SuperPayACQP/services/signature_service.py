"""
Signature Service for Alipay+ API
Handles RSA-SHA256 signature generation and verification
"""
import base64
import logging
from urllib.parse import quote, unquote
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from typing import Union, Optional, cast

logger = logging.getLogger(__name__)


class SignatureService:
    """
    Handles RSA-SHA256 signature generation and verification for Alipay+ API
    """
    
    def __init__(self, private_key: str, public_key: str, client_id: str):
        """
        Initialize the signature service
        
        Args:
            private_key: Base64 encoded PKCS#8 private key
            public_key: Base64 encoded X.509 public key
            client_id: Client identifier for Alipay+
        """
        self.private_key: rsa.RSAPrivateKey = self._load_private_key(private_key)
        self.public_key: rsa.RSAPublicKey = self._load_public_key(public_key)
        self.client_id = client_id
    
    def _load_private_key(self, key_str: str) -> rsa.RSAPrivateKey:

        try:
            # Try PEM format first (has headers)

            key_bytes = base64.b64decode(key_str)
            key = serialization.load_der_private_key(
                    key_bytes, 
                    password=None, 
                    backend=default_backend()
                )
            
            if not isinstance(key, rsa.RSAPrivateKey):
                raise ValueError("Private key must be an RSA key")
            return key
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise
    
    def _load_public_key(self, key_str: str) -> rsa.RSAPublicKey:
        """
        Load X.509 public key from Base64 string
        
        Args:
            key_str: Base64 encoded public key
            
        Returns:
            RSAPublicKey object
        """
        try:
            key_bytes = base64.b64decode(key_str)
            key = serialization.load_der_public_key(
                key_bytes, 
                backend=default_backend()
            )
            if not isinstance(key, rsa.RSAPublicKey):
                raise ValueError("Public key must be an RSA key")
            return cast(rsa.RSAPublicKey, key)
        except Exception as e:
            logger.error(f"Failed to load public key: {e}")
            raise
    
    def generate_request_signature(self, http_method: str, request_uri: str, 
                          request_time: str, request_body: str) -> str:
        """
        Generate signature for request
        
        Args:
            http_method: HTTP method (e.g., POST)
            request_uri: Request URI path
            request_time: UTC timestamp in ISO format
            request_body: Raw JSON request body
            
        Returns:
            URL-encoded Base64 signature
        """
        # Build content to be signed
        encoded_uri=quote(request_uri, safe='')
        content = f"{http_method.upper()} {encoded_uri}\n{self.client_id}.{request_time}.{request_body}"
        

        
        # Sign the content
        signature = self.private_key.sign(
            content.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        # Base64 URL-safe encode (keeps padding for proper decoding)
        # Note: base64.urlsafe_b64encode uses '-' and '_' instead of '+' and '/'
        generated_signature = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
        return generated_signature
    def generate_response_signature(self, http_method: str, response_uri: str, 
                          response_time: str, response_body: str) -> str:
        # Build content to be signed
        encoded_uri=quote(response_uri, safe='')
        content = f"{http_method.upper()} {encoded_uri}\n{self.client_id}.{response_time}.{response_body}"
        
        # Sign the content
        signature = self.private_key.sign(
            content.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        generated_signature = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
        return generated_signature
    def verify_signature(self, http_method: str, request_uri: str,
                        request_time: str, request_body: str, signature: str) -> bool:
        """
        Verify signature from response
        
        Args:
            http_method: HTTP method
            request_uri: Request URI path
            request_time: UTC timestamp
            request_body: Raw JSON response body
            signature: URL-encoded Base64 signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        content = ""  # Initialize before try block to avoid unbound variable
        try:
            # Build content to be validated
            content = f"{http_method.upper()} {request_uri}\n{self.client_id}.{request_time}.{request_body}"
            
            logger.debug(f"Signature verification - content length: {len(content)}")
            logger.debug(f"Signature verification - client_id: {self.client_id}")
            logger.debug(f"Signature verification - request_time: {request_time}")
            logger.debug(f"Signature verification - request_body length: {len(request_body)}")
            logger.debug(f"Signature verification - signature: {signature[:50]}...")
            
            # Decode signature
            signature_bytes = base64.urlsafe_b64decode(unquote(signature))
            
            # Verify signature
            self.public_key.verify(
                signature_bytes,
                content.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            logger.info("Signature verification successful")
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            logger.debug(f"Signature verification failed - content preview: {content[:200] if content else 'N/A'}...")
            return False
    
    def build_signature_header(self, signature: str, key_version: int = 1) -> str:
        """
        Build signature header value
        
        Args:
            signature: URL-encoded Base64 signature
            key_version: Key version number
            
        Returns:
            Signature header value
        """
        return f"algorithm=RSA256,keyVersion={key_version},signature={signature}"
    
    def extract_signature_from_header(self, header: str) -> Optional[str]:
        """
        Extract signature value from header
        
        Args:
            header: Signature header value
            
        Returns:
            Signature value or None if not found
        """
        if not header:
            return None
            
        for part in header.split(','):
            part = part.strip()
            if part.startswith('signature='):
                return part[len('signature='):]
        return None
