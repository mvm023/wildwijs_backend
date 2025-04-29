from django.core.management.base import BaseCommand
from api.image_scrape_api import scrape_images_for_organisms
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Scrape and upload images for organisms'

    def handle(self, *args, **kwargs):
        bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")

        if not bucket_name:
            self.stderr.write("Environment variable AWS_STORAGE_BUCKET_NAME not set.")
            return
        
        self.stdout.write(f"Using S3 bucket: {bucket_name}")
        
        # Call the function to scrape and upload images
        scrape_images_for_organisms(bucket_name=bucket_name)
