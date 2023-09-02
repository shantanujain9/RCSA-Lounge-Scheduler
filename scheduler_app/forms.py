from django import forms
from django.forms.widgets import FileInput

class MultiFileInput(FileInput):
    def value_from_datadict(self, data, files, name):
        return files.getlist(name)

class MultiFileUploadForm(forms.Form):
    files = forms.FileField(widget=MultiFileInput(), label="Upload multiple files", required=False)

'''
class UploadFileForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
'''