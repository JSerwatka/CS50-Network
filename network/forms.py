from django import forms
from .models import  Post, UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from flatpickr import DatePickerInput
from django_countries.widgets import CountrySelectWidget

class CreatePostForm(forms.ModelForm):
    content = forms.CharField(label="Description", widget=forms.Textarea(attrs={
                                    'placeholder': "What are you thinking about?",
                                    'autofocus': 'autofocus',
                                    'rows': '3',
                                    'class': 'form-control',
                                    'aria-label': "post content"
                             }))

    class Meta:
        model = Post
        fields = ["content"]

class CreateUserProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(required=False, label=_("Date of birth: "), widget=DatePickerInput(
        options = {
            "altFormat": "d F Y",
            "altInput": True,
            "dateFormat": "yyyy-mm-dd"
        },
    ))

    # Check if image doesn't exceed max file size
    def clean_image(self):
        image = self.cleaned_data.get('image')

        if "default.png" not in image:
            if image.size > 5*1024*1024:
                raise ValidationError("Image file too large ( > 5mb )")
        return image

    class Meta:
        model = UserProfile
        fields = ["name", "date_of_birth", "about", "country", "image"]
        labels = {
            "name": _("Name: "),
            "about": _("About: "),
            "country": _("Country: "),
            "image": _("Image: ")
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": _("Your name..."),
                "aria-label": _("your name"),
                "class": "form-control"
                }),
            "about": forms.Textarea(attrs={
                "placeholder": _("Tell about yourself..."),
                "aria-label": _("tell about yourself"),
                "class": "form-control"
                }),
            'country': CountrySelectWidget(
                 attrs={"class": "form-control"}
            ),
            "image": forms.FileInput(
                attrs={"class": "form-control-file"}
            )
        }