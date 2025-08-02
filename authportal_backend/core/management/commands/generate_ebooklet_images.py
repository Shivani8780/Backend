from django.core.management.base import BaseCommand

from authportal_backend.core.models import EBooklet
from authportal_backend.core.utils import generate_pdf_page_images

class Command(BaseCommand):
    help = 'Batch process all ebooklets to generate page images for PDFs'

    def handle(self, *args, **options):
        import os
        from django.conf import settings

        ebooklets = EBooklet.objects.all()
        total = ebooklets.count()
        self.stdout.write(f'Starting image generation for {total} ebooklets...')
        for ebooklet in ebooklets:
            try:
                page_images_dir = os.path.join(settings.MEDIA_ROOT, 'ebooklet_pages', str(ebooklet.id))
                if os.path.exists(page_images_dir) and os.listdir(page_images_dir):
                    self.stdout.write(self.style.NOTICE(f'Skipping ebooklet ID {ebooklet.id} - {ebooklet.name} (images already exist)'))
                    continue

                self.stdout.write(f'Processing ebooklet ID {ebooklet.id} - {ebooklet.name}...')
                generate_pdf_page_images(ebooklet)
                self.stdout.write(self.style.SUCCESS(f'Successfully generated images for ebooklet ID {ebooklet.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing ebooklet ID {ebooklet.id}: {e}'))
        self.stdout.write('Image generation batch process completed.')
