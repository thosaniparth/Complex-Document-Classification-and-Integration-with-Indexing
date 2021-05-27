
from django import forms
from .models import PostModel
from django.conf import settings


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class POSTform(forms.ModelForm):
    name=forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder":"First Name",}
        ),
    )
    middlename=forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder":"Middle Name",}
        ),
    )
    surname=forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder":"Last Name",}
        ),
    )
    # dob=forms.DateField(
    #     required=True,
    #     widget=forms.SelectDateWidget(
    #         attrs={"placeholder":"Date of Birth",}
    #     ),
         
    # )
    dob = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    image=forms.ImageField(required=True,widget=forms.ClearableFileInput(attrs={'multiple': False}))
    image1=forms.ImageField(required=True,widget=forms.ClearableFileInput(attrs={'multiple': False}))
    
    class Meta:
        model = PostModel
        fields = ('name', 'middlename','surname','dob', 'image','image1')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))