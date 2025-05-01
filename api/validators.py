import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_('Wachtwoord moet minstens één hoofdletter bevatten.'))
        if not re.search(r'\d', password):
            raise ValidationError(_('Wachtwoord moet minstens één getal bevatten.'))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(_('Wachtwoord moet minstens één speciaal karakter bevatten.'))