from django import forms
from .models import Text

PHRASE_MY_CHOICE = "Use my own choice"


class InputForm(forms.Form):
    titles = list(Text.objects.values_list('title'))
    titles = [(PHRASE_MY_CHOICE, PHRASE_MY_CHOICE)] + [(item[0], item[0]) for item in titles]
    source = forms.ChoiceField(choices=titles, initial=PHRASE_MY_CHOICE)
    user_text = forms.CharField(widget=forms.Textarea, label="Input your own text", required=False)
    sentence = forms.CharField(label="Start")
    length = forms.IntegerField(min_value=1, max_value=200)

    def __init__(self, *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)

        if self.data and self.data.get('source') == PHRASE_MY_CHOICE:
            self.fields.get('user_text').required = True

