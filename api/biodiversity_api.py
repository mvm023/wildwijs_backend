import requests
from .models import Classification, Organism

# API endpoint
baseURL = "https://api.biodiversitydata.nl/v2/"

query_params = {
    "defaultClassification.className": "Aves",  # Birds (Aves)
    "sourceSystem.code": "NSR",
    "_size": 1000,
}

response = requests.get(f"{baseURL}taxon/query", params=query_params)

if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")  # Print error message

try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print("Response is not valid JSON:", response.text)


for item in data["resultSet"]:
    taxon = item["item"]
    scientific_name = taxon["acceptedName"]["fullScientificName"]

    # Initialize fields
    organism_name = None
    alternative_names = []
    description = ""
    classification_values = {
        "species": "",
        "genus": "",
        "family": "",
        "order": "",
        "class_name": "",
        "phylum": "",
        "kingdom": ""
    }

    # Extract names if available
    if 'vernacularNames' in taxon:
        for vernacular in taxon["vernacularNames"]:
            if vernacular.get("language") == "Dutch":
                if vernacular.get("preferred"):
                    organism_name = vernacular.get("name", "")
                else:
                    alternative_names.append(vernacular.get("name", ""))
    else:
        continue

    # Extract occurrence status
    occurrence_status_verbatim = ""
    if "occurrenceStatusVerbatim" in taxon:
        occurrence_status_verbatim = taxon["occurrenceStatusVerbatim"]

    # Extract description if it exists
    if 'descriptions' in taxon:
        for desc in taxon["descriptions"]:
            if desc.get("category") == "Samenvatting" and desc.get("language") == "Dutch":
                description = desc.get("description", "")    

    # Extract classification from systemClassification
    if "systemClassification" not in taxon:
        continue
    else:
        for classification in taxon["systemClassification"]:
            rank = classification.get("rank")
            name = classification.get("name")

            # Map classification rank to corresponding field
            if rank == "species":
                classification_values["species"] = name
            elif rank == "genus":
                classification_values["genus"] = name
            elif rank == "familia":
                classification_values["family"] = name
            elif rank == "ordo":
                classification_values["order"] = name
            elif rank == "classis":
                classification_values["class_name"] = name
            elif rank == "phylum":
                classification_values["phylum"] = name
            elif rank == "regnum":
                classification_values["kingdom"] = name

    if Organism.objects.filter(name=organism_name).exists():
        print(f"Organism {organism_name} already exists, skipping.")
        continue  # Skip to the next iteration

    # Get or create Classification object
    classification, created = Classification.objects.get_or_create(
        species=classification_values["species"],
        genus=classification_values["genus"],
        family=classification_values["family"],
        order=classification_values["order"],
        class_name=classification_values["class_name"],
        phylum=classification_values["phylum"],
        kingdom=classification_values["kingdom"]
    )

    # Create or update the Organism object
    organism, created = Organism.objects.update_or_create(
        scientific_name=scientific_name,  # Use scientific_name to uniquely identify
        defaults={
            'name': organism_name,  # If no name found, use scientific_name
            'description': description if description else "",  # Empty string if no description
            'classification': classification,
            'occurrence_status_verbatim': occurrence_status_verbatim,
            'alternative_names': alternative_names  # List of alternative names
        }
    )

    print(f"Organism '{organism_name}' created/updated.")
