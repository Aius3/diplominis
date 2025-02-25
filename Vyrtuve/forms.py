from django import forms
from django.contrib.auth.models import User
from .models import Profilis, Receptas, Sablonas, Raktazodis, Reitingas, Komentaras


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profilis
        fields = ['vardas', 'aprasas', 'nuotrauka']


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Receptas
        fields = ['titulas', 'aprasas', 'ingridientai', 'instrukcijos', 'nuotrauka', 'gaminimo_laikas', 'ar_veganiskas',
                  'ar_vegetariskas', 'sablonas']

    sablonas = forms.ModelChoiceField(queryset=Sablonas.objects.all(), empty_label=None)

    ar_veganiskas = forms.BooleanField(required=False)
    ar_vegetariskas = forms.BooleanField(required=False)

    raktazodziai = forms.ModelMultipleChoiceField(
        queryset=Raktazodis.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Komentaras
        fields = ['turinys', ]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Reitingas
        fields = ['reitingas', 'favoritas']

    favoritas = forms.BooleanField(required=False)
