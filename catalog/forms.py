from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms

from django.core.validators import EMPTY_VALUES

from .models import *

txtbox_cols = 40
txtbox_rows = 2

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateRecordForm(ModelForm):
    class Meta:
        model = Record
        
        fields = ['my_catalog', 'name', 'acquisition_date', 'creation_date', 'manufacturer','record_picture', 'condition_rating', 'condition_description',  'description', ]
        labels = { 'my_catalog': 'Catalog', 'record_picture': 'Picture' }
        widgets = {           
            'description': forms.Textarea(attrs={'rows':txtbox_rows, 'cols':txtbox_cols}),
            'condition_description': forms.Textarea(attrs={'rows':txtbox_rows, 'cols':txtbox_cols}),
        }


class CreateCatalogForm(ModelForm):
    class Meta:
        model = Catalog
        fields = ['name', 'description']


class CreateProvenanceForm(ModelForm):
    class Meta:
        model = Provenance
        fields = ['record', 'date', 'owner', 'nation']


class CreateManufacturerForm(ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']


class SearchForm(forms.Form):
    searchString = forms.CharField(max_length=100)


class CustomFieldForm(ModelForm):
    class Meta:
        model = CustomField
        exclude = ['record']
        widgets = {
            'cf_text': forms.Textarea(attrs={'rows':txtbox_rows, 'cols':txtbox_cols})
        }

    def clean(self):
        type = self.cleaned_data.get('type')
        field_label = self.cleaned_data.get('field_label')
        cf_char = self.cleaned_data.get('cf_char')
        cf_text = self.cleaned_data.get('cf_text')
        cf_bool = self.cleaned_data.get('cf_bool')
        cf_int = self.cleaned_data.get('cf_int')
        cf_dec = self.cleaned_data.get('cf_dec')

        if '' == field_label:
            if ('char' == type and '' != cf_char) or (
                    'text' == type and '' != cf_text) or (
                    'bool' == type and None != cf_bool) or (
                    'int' == type and None != cf_int) or (
                    'dec' == type and None != cf_dec):
                self._errors['field_label'] = self.error_class([
                    'Field Label Required!'])
        return self.cleaned_data
