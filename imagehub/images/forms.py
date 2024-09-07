from django import forms

from .models import Image, Category


class ImageUploadForm(forms.ModelForm):
    file = forms.ImageField(
        label='File',
        widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'hidden-file-input'}),
        required=True
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Select category'}),
        empty_label="Select category",
        required=True
    )

    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add a description to your image',
            'style': 'height: 200px'
        }),
        required=False
    )

    class Meta:
        model = Image
        fields = ['file', 'category', 'description']


class ImageEditForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Select category'}),
        empty_label="Select category",
        required=True
    )

    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add a description to your image',
            'style': 'height: 200px'
        }),
        required=False
    )

    class Meta:
        model = Image
        fields = ['category', 'description']
