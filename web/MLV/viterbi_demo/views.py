from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.urlresolvers import reverse

import my_little_viterbi
from .forms import InputForm


def index(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            raw_text = my_little_viterbi.process_file(file_name="orwell.txt")
            output = my_little_viterbi.start(
                raw_text=raw_text,
                user_sentence=form.cleaned_data['sentence'],
                length=form.cleaned_data['length'],
                is_debug=False)
            form = InputForm(request.POST)
            return render(request, 'viterbi_demo/index.html', {'output': output, "form": form})
    else:
        form = InputForm()
    return render(request, 'viterbi_demo/index.html', {'form': form})


