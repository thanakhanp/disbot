# utils.py

def is_image(attachment):
    if attachment.content_type and attachment.content_type.startswith('image/'):
        return True
    image_ext = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    return attachment.filename.lower().endswith(image_ext)
