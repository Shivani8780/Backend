from django.core.management.base import BaseCommand
from authportal_backend.core.models import EBooklet
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Create ebooklets for all PDF files'

    def handle(self, *args, **options):
        # Define the ebooklets to create based on your PDF files
        ebooklets_data = [
            {'name': 'B1 Boys', 'static_pdf_filename': 'B1 Boys.pdf'},
            {'name': 'B2 Boys', 'static_pdf_filename': 'B2 Boys.pdf'},
            {'name': 'B3 Boys', 'static_pdf_filename': 'B3 Boys.pdf'},
            {'name': 'Divorce Boys', 'static_pdf_filename': 'Divorce Boys.pdf'},
            {'name': 'Divorce Girls', 'static_pdf_filename': 'Divorce Girls.pdf'},
            {'name': 'Gujarat Girls', 'static_pdf_filename': 'Gujarat Girls.pdf'},
            {'name': 'MMR Boys', 'static_pdf_filename': 'MMR Boys.pdf'},
            {'name': 'MMR Girls', 'static_pdf_filename': 'MMR Girls.pdf'},
            {'name': 'NRI Boys', 'static_pdf_filename': 'NRI Boys.pdf'},
            {'name': 'NRI Girls', 'static_pdf_filename': 'NRI Girls.pdf'},
            {'name': 'Saurashtra Girls', 'static_pdf_filename': 'Saurashtra Girls.pdf'},
            {'name': 'Saurashtra Boys', 'static_pdf_filename': 'Saurashtra Boys.pdf'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for ebooklet_data in ebooklets_data:
            # Check if ebooklet already exists
            ebooklet, created = EBooklet.objects.get_or_create(
                name=ebooklet_data['name'],
                defaults={
                    'static_pdf_filename': ebooklet_data['static_pdf_filename']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created ebooklet: "{ebooklet.name}" -> {ebooklet.static_pdf_filename}'
                    )
                )
            else:
                # Update static_pdf_filename if it's not set
                if not ebooklet.static_pdf_filename:
                    ebooklet.static_pdf_filename = ebooklet_data['static_pdf_filename']
                    ebooklet.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Updated ebooklet: "{ebooklet.name}" -> {ebooklet.static_pdf_filename}'
                        )
                    )
                else:
                    self.stdout.write(
                        f'Ebooklet already exists: "{ebooklet.name}"'
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Ebooklets creation completed! Created: {created_count}, Updated: {updated_count}'
            )
        )
