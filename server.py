import uvicorn
import os
from src.main import app

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server with production settings
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        workers=4,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    ) 