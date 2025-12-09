from django import forms
from .models import ExamPaper

class ExamPaperForm(forms.ModelForm):
    class Meta:
        model = ExamPaper
        fields = ['title', 'source_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
                'placeholder': '例如：计算机网络期末复习'
            }),
            'source_file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                'accept': '.txt' # currently only supporting txt in parser
            })
        }
