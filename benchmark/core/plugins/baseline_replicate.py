from PIL import Image, ImageDraw
import os
import requests
import replicate
from io import BytesIO

# Model constants
FACE_SWAP_MODEL = "cdingram/face-swap"
FACE_SWAP_VERSION = "d1d6ea8c8be89d664a07a457526f7128109dee7030fdac424788d762c71ed111"

def create_error_image(error_text, details=None):
    """Create an error image with the specified text."""
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

def generate(case):
    """
    Generate an image for a test case using Replicate's face-swap model.
    This is a direct face-swapping tool specifically designed for this purpose.
    Uses Replicate's Python client for simplicity and reliability.
    """
    # Ensure API key is available
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_api_token:
        print("Replicate: REPLICATE_API_TOKEN environment variable not set")
        return create_error_image("Error: REPLICATE_API_TOKEN not set")

    # Extract case details
    case_id = case.get('id', 'unknown')
    template_path = case.get('template_image')
    avatar_paths = case.get('avatars', [])
    
    # Verify required inputs
    if not template_path or not os.path.exists(template_path):
        print(f"Replicate: Missing template image for case: {case_id}")
        return create_error_image("Error: Missing template image")
    
    if not avatar_paths or not os.path.exists(avatar_paths[0]):
        print(f"Replicate: Missing avatar image for case: {case_id}")
        return create_error_image("Error: Missing avatar image")
    
    # Log what we're doing
    print(f"Replicate: Processing case: {case_id}")
    print(f"Replicate: Using template at: {template_path}")
    print(f"Replicate: Using avatar at: {avatar_paths[0]}")
    
    try:
        # The Replicate Python client handles file uploads automatically
        print("Replicate: Starting face swap process...")
        
        # Prepare input for the model
        input_params = {
            "input_image": open(template_path, "rb"),
            "swap_image": open(avatar_paths[0], "rb")
        }
        
        # Run the model
        result = replicate.run(
            f"{FACE_SWAP_MODEL}:{FACE_SWAP_VERSION}", 
            input=input_params
        )
        
        if not result:
            print(f"Replicate: Face swap failed for case: {case_id}")
            return create_error_image("Error: Face swap failed", "No output received from model")
        
        print(f"Replicate: Face swap completed successfully for case: {case_id}")
        print(f"Replicate: Output URL: {result}")
        
        # Download the result image
        response = requests.get(result)
        response.raise_for_status()
        
        # Return as PIL Image
        return Image.open(BytesIO(response.content))
        
    except Exception as e:
        print(f"Replicate: Error generating image for case: {case_id}")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return create_error_image("Error:", str(e))