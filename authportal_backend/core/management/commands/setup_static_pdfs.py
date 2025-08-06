from django.core.management.base import BaseCommand
from authportal_backend.core.models import EBooklet
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Set up static PDF filenames for existing ebooklets'

    def handle(self, *args, **options):
        # Define the mapping of ebooklet names to static PDF filenames
        pdf_mapping = {
            'B1 Boys': 'B1 Boys.pdf',
            'B1_Boys': 'B1 Boys.pdf',
            'B2 Boys': 'B2 Boys.pdf',
            'B2_Boys': 'B2 Boys.pdf',
            'B3 Boys': 'B3 Boys.pdf',
            'B3_Boys': 'B3 Boys.pdf',
            'Divorce Boys': 'Divorce Boys.pdf',
            'Divorce_Boys': 'Divorce Boys.pdf',
            'Divorce Girls': 'Divorce Girls.pdf',
            'Divorce_Girls': 'Divorce Girls.pdf',
            'Gujarat Girls': 'Gujarat Girls.pdf',
            'Gujarat_Girls': 'Gujarat Girls.pdf',
            'MMR Boys': 'MMR Boys.pdf',
            'MMR_Boys': 'MMR Boys.pdf',
            'MMR Girls': 'MMR Girls.pdf',
            'MMR_Girls': 'MMR Girls.pdf',
            'NRI Boys': 'NRI Boys.pdf',
            'NRI_Boys': 'NRI Boys.pdf',
            'NRI Girls': 'NRI Girls.pdf',
            'NRI_Girls': 'NRI Girls.pdf',
            'Saurashtra Girls': 'Saurashtra Girls.pdf',
            'Saurashtra_Girls': 'Saurashtra Girls.pdf',
            'Saurashtra Boys': 'Saurasthra Boys.pdf',
            'Saurashtra_Boys': 'Saurasthra Boys.pdf',
        }
        
        # Get all ebooklets
        ebooklets = EBooklet.objects.all()
        
        self.stdout.write(f"Found {ebooklets.count()} ebooklets to process")
        
        for ebooklet in ebooklets:
            # Try to find a matching PDF filename
            static_filename = None
            
            # First, try exact name match
            if ebooklet.name in pdf_mapping:
                static_filename = pdf_mapping[ebooklet.name]
            else:
                # Try partial matches
                for key, filename in pdf_mapping.items():
                    if key.lower() in ebooklet.name.lower() or ebooklet.name.lower() in key.lower():
                        static_filename = filename
                        break
            
            if static_filename:
                # Check if the static PDF file actually exists
                static_pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdfs', static_filename)
                if os.path.exists(static_pdf_path):
                    ebooklet.static_pdf_filename = static_filename
                    ebooklet.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated ebooklet "{ebooklet.name}" (ID: {ebooklet.id}) -> {static_filename}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Static PDF file not found for ebooklet "{ebooklet.name}": {static_pdf_path}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No matching static PDF found for ebooklet "{ebooklet.name}" (ID: {ebooklet.id})'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('Static PDF setup completed!'))
