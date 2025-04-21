from PIL import Image

def read_image(path: str) -> Image.Image:
    """Read an image from disk."""
    return Image.open(path)

def save_image(image: Image.Image, path: str):
    """Save an image to disk."""
    image.save(path)