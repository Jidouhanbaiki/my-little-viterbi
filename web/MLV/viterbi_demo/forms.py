from django import forms
from .models import Text

PHRASE_MY_CHOICE = "Use my own choice"


class InputForm(forms.Form):
    titles = list(Text.objects.values_list('title'))
    titles = [(PHRASE_MY_CHOICE, PHRASE_MY_CHOICE)] + [(item[0], item[0]) for item in titles]
    source = forms.ChoiceField(choices=titles, initial=PHRASE_MY_CHOICE)
    sentence = forms.CharField(label="Start")
    length = forms.IntegerField(min_value=1, max_value=200)
