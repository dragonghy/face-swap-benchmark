"""
Face swap implementation using Replicate's face-swap model.

This plugin provides integration with Replicate's face-swap model to perform 
face swapping operations for the benchmark framework.
"""

from PIL import Image, ImageDraw
import os
import logging
import requests
import replicate
from io import BytesIO
from typing import Dict, List, Optional, Any, Union

# Model constants
FACE_SWAP_MODEL = "cdingram/face-swap"
FACE_SWAP_VERSION = "d1d6ea8c8be89d664a07a457526f7128109dee7030fdac424788d762c71ed111"

# Configure logger
logger = logging.getLogger(__name__)

def create_error_image(error_text: str, details: Optional[str] = None) -> Image.Image:
    """
    Create an error image with the specified text.
    
    Args:
        error_text: The primary error message to display
        details: Optional detailed error message
        
    Returns:
        A PIL Image containing the error message
    """
    img = Image.new('RGB', (512, 512), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), error_text, fill=(255, 0, 0))
    
    if details:
        # Split error message into multiple lines if it's long
        if len(details) > 100:
            for i in range(0, len(details), 100):
                draw.text((10, 30 + i//5), details[i:i+100], fill=(0, 0, 0))
        else:
            draw.text((10, 30), details, fill=(0, 0, 0))
    
    return img

def generate(case: Dict[str, Any]) -> Image.Image:
    """
    Generate an image for a test case using Replicate's face-swap model.
    
    This plugin uses Replicate's Python client to perform face swapping operations.
    It takes the template image and the first avatar from the case and swaps faces.
    
    Args:
        case: A dictionary containing test case details including template_image and avatars
        
    Returns:
        A PIL Image with the face swap result
    """
    # Ensure API key is available
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_api_token:
        logger.error("REPLICATE_API_TOKEN environment variable not set")
        return create_error_image("Error: REPLICATE_API_TOKEN not set")

    # Extract case details
    case_id = case.get('id', 'unknown')
    template_path = case.get('template_image')
    avatar_paths = case.get('avatars', [])
    
    # Verify required inputs
    if not template_path or not os.path.exists(template_path):
        logger.error(f"Missing template image for case: {case_id}")
        return create_error_image("Error: Missing template image")
    
    if not avatar_paths or not os.path.exists(avatar_paths[0]):
        logger.error(f"Missing avatar image for case: {case_id}")
        return create_error_image("Error: Missing avatar image")
    
    # Log what we're doing
    logger.info(f"Processing case: {case_id}")
    logger.info(f"Using template at: {template_path}")
    logger.info(f"Using avatar at: {avatar_paths[0]}")
    
    try:
        # The Replicate Python client handles file uploads automatically
        logger.info("Starting face swap process...")
        
        # Prepare input for the model
        with open(template_path, "rb") as template_file, open(avatar_paths[0], "rb") as avatar_file:
            input_params = {
                "input_image": template_file,
                "swap_image": avatar_file
            }
            
            # Run the model
            result = replicate.run(
                f"{FACE_SWAP_MODEL}:{FACE_SWAP_VERSION}", 
                input=input_params
            )
        
        if not result:
            logger.error(f"Face swap failed for case: {case_id} - No output received")
            return create_error_image("Error: Face swap failed", "No output received from model")
        
        logger.info(f"Face swap completed successfully for case: {case_id}")
        logger.debug(f"Output URL: {result}")
        
        # Download the result image
        response = requests.get(result, timeout=30)
        response.raise_for_status()
        
        # Return as PIL Image
        return Image.open(BytesIO(response.content))
        
    except Exception as e:
        logger.exception(f"Error generating image for case: {case_id}")
        return create_error_image("Error:", str(e))