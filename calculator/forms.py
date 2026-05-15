from django import forms
from .models import DetailJournee, Employe
import re

class AccessCodeForm(forms.Form):
    access_code = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le code d\'accès',
            'autocomplete': 'off'
        })
    )
    
    def clean_access_code(self):
        code = self.cleaned_data['access_code']
        # Validation basique pour éviter les injections
        if re.search(r'[<>{}]', code):
            raise forms.ValidationError('Code invalide')
        return code

class DetailJourneeForm(forms.ModelForm):
    class Meta:
        model = DetailJournee
        fields = ['frais_local', 'frais_electricite_impots']
        widgets = {
            'frais_local': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'frais_electricite_impots': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'frais_local': 'Frais de local (DA)',
            'frais_electricite_impots': 'Électricité & Impôts (DA)',
        }

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'salaire_journalier']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'employé'
            }),
            'salaire_journalier': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Salaire en DA'
            }),
        }
    
    def clean_nom(self):
        nom = self.cleaned_data['nom']
        if re.search(r'[<>{}]', nom):
            raise forms.ValidationError('Nom invalide')
        return nom