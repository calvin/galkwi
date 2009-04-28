# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ValidationError
from galkwi.models import *
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _

class UserRegistrationForm(forms.Form):
    agree = forms.BooleanField(label=u'위 사항에 동의합니다')

class EntrySearchForm(forms.Form):
    word = forms.CharField(label=u'단어')

class ProposalVoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['vote', 'reason']

class ProposalCancelForm(forms.Form):
    pass

error_messages = {
    'required': _(u'This field is required.'),
    'invalid': _(u'Enter a valid value.'),
}

class ProposalEditAddForm(forms.ModelForm):
    def clean_word(self):
        word = self.cleaned_data.get('word')
        if not word:
            raise ValidationError(error_messages['required'])
        return word
    def clean_pos(self):
        pos = self.cleaned_data.get('pos')
        if not pos:
            raise ValidationError(error_messages['required'])
        return pos
        
    class Meta:
        model = Proposal
        exclude = ['word_substrings',
                   'action', 'date', 'editor', 'status', 'new_entry',
                   'old_entry', 'status_date']

class ProposalEditRemoveForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['rationale']

class ProposalEditUpdateForm(forms.ModelForm):
    def clean_word(self):
        word = self.cleaned_data.get('word')
        if not word:
            raise ValidationError(error_messages['required'])
        return word
    def clean_pos(self):
        pos = self.cleaned_data.get('pos')
        if not pos:
            raise ValidationError(error_messages['required'])
        return pos
        
    class Meta:
        model = Proposal
        exclude = ['word_substrings',
                   'action', 'date', 'editor', 'status', 'new_entry',
                   'old_entry', 'status_date']
