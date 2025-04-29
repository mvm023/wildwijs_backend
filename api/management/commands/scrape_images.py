from django.core.management.base import BaseCommand
from api.image_scrape_api import scrape_images_for_organisms
from django.conf import settings

class Command(BaseCommand):
    help = 'Scrape and upload images for organisms'

    def handle(self, *args, **kwargs):
        # Use different bucket for production vs development
        bucket_name = "wildwijs-images-prod" if settings.ENVIRONMENT == "production" else "wildwijs-images-dev"
        
        self.stdout.write(f"Using S3 bucket: {bucket_name}")
        
        # Call the function to scrape and upload images
        scrape_images_for_organisms(bucket_name=bucket_name)
