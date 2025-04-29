from django.core.management.base import BaseCommand
from biodiversity_api import import_organisms
from django.conf import settings


class Command(BaseCommand):
    help = 'Import organisms from external API'

    def add_arguments(self, parser):
        # Adding both class_name and order as optional arguments
        parser.add_argument(
            '--class_name',
            type=str,
            help='Class name to filter organisms (e.g., Aves)',
        )
        parser.add_argument(
            '--order',
            type=str,
            help='Order to filter organisms (e.g., Falconiformes)',
        )

    def handle(self, *args, **kwargs):
        class_name = kwargs['class_name']
        order = kwargs['order']

        # Provide feedback if both arguments are missing
        if not class_name and not order:
            self.stdout.write("Please specify at least one filter: --class_name or --order")
            return

        # Show feedback to indicate which filters are being used
        if class_name:
            self.stdout.write(f"Starting import for class: {class_name}")
        if order:
            self.stdout.write(f"Starting import for order: {order}")
        
        # Call the import_organisms function with the given filters
        import_organisms(class_name=class_name, order=order)