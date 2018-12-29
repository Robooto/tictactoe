from django.forms import ModelForm
from .models import Invitation


# creating class for the form and using meta to define the form specifically
class InvitationForm(ModelForm):
    class Meta:
        model = Invitation
        exclude = ('from_user', 'timestamp')
