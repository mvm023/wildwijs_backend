import requests
from bs4 import BeautifulSoup
from .models import Organism
import re
import os
import boto3
from botocore.exceptions import NoCredentialsError

def fetch_best_image_from_observation_org(scientific_name):
    """ Fetch the best species image URL from observation.org using scientific name and photo likes. """
    
    # Step 1: Search for the species using the scientific name
    search_url = f"https://observation.org/search/?q={scientific_name.replace(' ', '+')}"
    
    response = requests.get(search_url)
    if response.status_code != 200:
        print(f"Failed to search for {scientific_name}. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Step 2: Extract species ID
    species_link = soup.find('a', {'href': re.compile(r'^/species/\d+/')})
    if not species_link:
        print(f"No species link found for {scientific_name}")
        return None
    
    species_id = species_link.attrs['href'].split('/')[2]
    print(f"Species id for {scientific_name} is {species_id}")
    

    
    photos_url = f"https://observation.org/species/{species_id}/"
    response = requests.get(photos_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch page for species={scientific_name}. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    img_tags = soup.find_all('a')

    image_url = None
    for img in img_tags:
        src = img.get('href')
        if src:
            if src.startswith('/media/photo/') and '.jpg' in src:
                image_url = f"https://observation.org{src}"
                break  # Take the first valid image

    return image_url

def download_image(image_url, folder='/tmp'):
    """Download an image from a URL and save it to a temporary folder."""

    # Make the request to download the image
    response = requests.get(image_url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download image: {image_url}")

    # Extract filename from the URL (remove query parameters)
    filename = os.path.basename(image_url)
    filename = re.sub(r'\?.*$', '', filename)  # Remove query parameters

    # Ensure the filename is safe and doesn't have any unwanted characters
    filename = filename.split('?')[0]  # Remove query parameters (if any)
    
    # Construct the local path to save the file
    local_path = os.path.join(folder, filename)

    # Write the image data to a local file
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    
    return local_path

def upload_to_s3(local_image_path, bucket_name):
    """Upload a file to an S3 bucket."""
    s3 = boto3.client('s3')  # Create an S3 client

    filename = os.path.basename(local_image_path)
    s3_path = f"organism-images/{filename}"

    try:
        # Upload the image to S3
        try:
            s3.upload_file(local_image_path, bucket_name, s3_path)
            print(f"Uploaded {local_image_path} to S3 as {s3_path}")
        except Exception as e:
            print(f"Upload failed for {local_image_path}: {e}")
                
        # Return the S3 URL of the uploaded image
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_path}"
        return s3_url

    except FileNotFoundError:
        print(f"File not found: {local_image_path}")
    except NoCredentialsError:
        print("Credentials not available for S3.")
    except Exception as e:
        print(f"An error occurred while uploading to S3: {e}")
    
    return None


def clean_scientific_name(name):
    """Extract just the genus and species from a full scientific name."""
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return name  # fallback in case it's weirdly formatted

def scrape_images_for_organisms():
    for organism in Organism.objects.all():
        if organism.name != "Oehoe":
            continue  # Already has an image

        scientific_name = clean_scientific_name(organism.scientific_name)
        image_url = fetch_best_image_from_observation_org(scientific_name)  # Scrape or API call
        
        if image_url:
            local_image = download_image(image_url)
            print(f"Downloaded image for {organism.name}")
            s3_url = upload_to_s3(local_image, "wildwijs-images-dev")
            organism.image_url = s3_url
            organism.save()
