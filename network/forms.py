from django import forms
from .models import  Post, Comment, UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from flatpickr import DatePickerInput
from django_countries.widgets import CountrySelectWidget

class CreatePostForm(forms.ModelForm):
    content = forms.CharField(label="Description", widget=forms.Textarea(attrs={
                                    'placeholder': _("What are you thinking about?"),
                                    'autofocus': 'autofocus',
                                    'rows': '3',
                                    'class': 'form-control',
                                    'aria-label': _("post content")
                             }))

    class Meta:
        model = Post
        fields = ["content"]

class CreateCommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
                                    'placeholder': _("Write a comment..."),
                                    'rows': '1',
                                    'class': 'form-control',
                                    'aria-label': _("comment content")
                             }))

    class Meta:
        model = Comment
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
            if image.size > settings.MAX_UPLOAD_SIZE * 1024 * 1024:
                raise ValidationError(_(f"Image file exceeds {settings.MAX_UPLOAD_SIZE} MB size limit"))
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
        }