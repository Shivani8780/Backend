import os
from pdf2image import convert_from_path
from django.conf import settings

def generate_pdf_page_images(ebooklet):
    """
    Generate PNG images for each page of the PDF file of the given ebooklet.
    Saves images in MEDIA_ROOT/ebooklet_pages/{ebooklet_id}/page_{page_num}.png
    Skips generation if images already exist (caching).
    """
    if not ebooklet.pdf_file:
        raise ValueError("Ebooklet has no PDF file to process.")

    pdf_path = ebooklet.pdf_file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, 'ebooklet_pages', str(ebooklet.id))
    os.makedirs(output_dir, exist_ok=True)

    # Check if images already exist (cache)
    existing_images = [f for f in os.listdir(output_dir) if f.startswith('page_') and f.endswith('.png')]
    if existing_images:
        # Images already generated, skip regeneration
        return output_dir

    # Convert PDF pages to images with higher DPI for better quality
    pages = convert_from_path(pdf_path, dpi=300, output_folder=output_dir, fmt='png', output_file='page')

    # Rename images to page_{page_num}.png
    for i, page in enumerate(pages, start=1):
        old_path = os.path.join(output_dir, f'page-{i:03d}.png')
        new_path = os.path.join(output_dir, f'page_{i}.png')
        if os.path.exists(old_path):
            os.rename(old_path, new_path)

    return output_dir
