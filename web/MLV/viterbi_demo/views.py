from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.urlresolvers import reverse
from django.contrib import messages


import my_little_viterbi
from .forms import InputForm, PHRASE_MY_CHOICE
from .models import Text


def index(request):

    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['source'] == PHRASE_MY_CHOICE:
                raw_text = form.cleaned_data['user_text']
            else:
                t = Text.objects.get(title__exact=form.cleaned_data['source'])
                raw_text = t.content
                form.cleaned_data['user_text'] = ""
            output = my_little_viterbi.start(
                raw_text=raw_text,
                user_sentence=form.cleaned_data['sentence'],
                length=form.cleaned_data['length'],
                is_debug=False)
            messages.add_message(request, messages.INFO, output)
            form = InputForm(request.POST)
            #return render(request, 'viterbi_demo/index.html', {'output': output, 'form': form})
            return HttpResponseRedirect(reverse('index'))

    else:
        form = InputForm()
    return render(request, 'viterbi_demo/index.html', {'form': form})


