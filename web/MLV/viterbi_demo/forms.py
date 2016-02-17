from django import forms


class InputForm(forms.Form):
    sentence = forms.CharField(label="Start")
    length = forms.IntegerField(min_value=1, max_value=200)
