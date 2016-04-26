from django import forms
from .models import Text

PHRASE_MY_CHOICE = "Use my own text"


class InputForm(forms.Form):
    titles = list(Text.objects.values_list('title'))
    titles = [(item[0], item[0]) for item in titles] + [(PHRASE_MY_CHOICE, PHRASE_MY_CHOICE)]
    source = forms.ChoiceField(
        choices=titles,
        initial=titles[0][0],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    user_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 80, 'style': 'resize: none',
                                                             'class': 'form-control'}),
                                label="Input your own text",
                                required=False)
    sentence = forms.CharField(label="Start with (type a word or a phrase)",
                               widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    length = forms.IntegerField(min_value=1, max_value=200,
                                widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)

        if self.data and self.data.get('source') == PHRASE_MY_CHOICE:
            self.fields.get('user_text').required = True

