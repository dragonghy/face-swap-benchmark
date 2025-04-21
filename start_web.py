#!/usr/bin/env python3
"""
Start script for the Face Swap Benchmark web interface.

This script starts the web interface on http://localhost:8000.
"""

import os
import logging
import argparse
import uvicorn
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("face_swap_benchmark")

def main():
    """Run the Face Swap Benchmark web interface."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Face Swap Benchmark Web Interface")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload when code changes"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("REPLICATE_API_TOKEN"):
        logger.warning("REPLICATE_API_TOKEN environment variable not set.")
        logger.warning("Face swapping functionality will not work without it.")
        logger.warning("Please set it in your environment or .env file.")
    
    # Set log level based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Print startup message
    logger.info("Starting Face Swap Benchmark Web Interface...")
    logger.info(f"Open your browser to http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    logger.info("Press Ctrl+C to exit")
    
    # Start the server
    uvicorn.run(
        "benchmark.web.main:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )

if __name__ == "__main__":
    main()