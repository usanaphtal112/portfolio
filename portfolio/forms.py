from django import forms


class ContactForm(forms.Form):
    project = forms.CharField(
        max_length=255, widget=forms.HiddenInput(), required=False
    )
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True, max_length=2000)
