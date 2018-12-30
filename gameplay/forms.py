from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Move


class MoveForm(ModelForm):
    class Meta:
        model = Move
        exclude = []  # need to have this but it can be empty

    def clean(self):
        """over riding clean function lets you do custom validation"""
        x = self.cleaned_data.get("x")
        y = self.cleaned_data.get("y")
        game = self.instance.game
        try:
            if game.board()[y][x] is not None:
                raise ValidationError("Square is not empty")
        except IndexError:
            raise ValidationError("Invalid coordinates")
        return self.cleaned_data
