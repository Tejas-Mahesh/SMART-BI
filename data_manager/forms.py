from django import forms
from .models import Dataset


class DatasetUploadForm(forms.ModelForm):

    class Meta:
        model = Dataset

        fields = [
            "name",
            "dataset_type",
            "file",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Example: Sales Data 2026",
                }
            ),

            "dataset_type": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),

            "file": forms.ClearableFileInput(
                attrs={
                    "class": "file-input",
                    "accept": ".csv,.xlsx,.xls",
                }
            ),
        }

    def clean_file(self):

        file = self.cleaned_data.get("file")

        if not file:
            raise forms.ValidationError(
                "Please select a file."
            )

        allowed_extensions = [
            ".csv",
            ".xlsx",
            ".xls",
        ]

        filename = file.name.lower()

        if not any(
            filename.endswith(ext)
            for ext in allowed_extensions
        ):
            raise forms.ValidationError(
                "Only CSV, XLSX and XLS files are supported."
            )

        # Maximum file size: 50 MB
        max_size = 50 * 1024 * 1024

        if file.size > max_size:
            raise forms.ValidationError(
                "File size cannot exceed 50 MB."
            )

        return file