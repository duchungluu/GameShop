from game.models import UserProfile, StoreGame
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

# forms.py tiedostossa luodaan luokkia, jotka toimivat HTML-formien tapaan.
# Tämä meinaa että kun meillä on jo "models.py", on tietokantaan menevien
# objektien form fieldit jo tiedossa. forms.py:n avulle ei siis tarvitse kirjoittaa
# erikseen html-koodia formeja varten, vaan formit luodaan automaattisesti tässä tiedostossa


class UserForm(forms.ModelForm):
    """Displayed when creating profile."""

    # Had to create a new form for the email, as the user.email was not required
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        }


class UserProfileForm(forms.ModelForm):
    """Displayed when viewing and changing profile."""
    class Meta:
        model = UserProfile
        fields = ('isDeveloper', 'picture')
        labels = {
            'isDeveloper': _('Do you want developer rights?'),
            'picture': _('Profile Picture'),
        }
        widgets = {
            'isDeveloper': forms.CheckboxInput(),
            'picture': forms.URLInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        }


class StoreGameForm(forms.ModelForm):
    """Displayed when adding a new game as a developer."""
    class Meta:
        model = StoreGame
        fields = ('title', 'desc', 'price', 'genre', 'imageUrl', 'url')
        widgets = {
            'title': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'desc': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'genre': forms.Select(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'imageUrl': forms.URLInput(attrs={'autocomplete': 'off', 'class': 'form-control'}),
            'url': forms.URLInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        }
