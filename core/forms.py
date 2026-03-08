from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Event, ClassLog, CustomUser, Student, Faculty

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title','description','date']
        widgets = {
            'date':forms.DateInput(attrs={'type':'date'})
        }

class ClassLogForm(forms.ModelForm):
    class Meta:
        model = ClassLog
        fields = ['date', 'subject', 'topics_covered', 'assignments']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'topics_covered': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Separate topics by commas for better AI video suggestions!'}),
            'assignments': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional homework assignments or reading.'})
        }

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-2 focus:ring-navy-500 focus:border-navy-500 block w-full sm:text-sm border-slate-300 rounded-lg py-2.5 px-4 font-medium bg-slate-50 focus:bg-white transition-all text-slate-800'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-2 focus:ring-navy-500 focus:border-navy-500 block w-full sm:text-sm border-slate-300 rounded-lg py-2.5 px-4 font-medium bg-slate-50 focus:bg-white transition-all text-slate-800'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'shadow-sm focus:ring-2 focus:ring-navy-500 focus:border-navy-500 block w-full sm:text-sm border-slate-300 rounded-lg py-2.5 px-4 font-medium bg-slate-50 focus:bg-white transition-all text-slate-800'}))
    roll_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-2 focus:ring-navy-500 focus:border-navy-500 block w-full sm:text-sm border-slate-300 rounded-lg py-2.5 px-4 font-medium bg-slate-50 focus:bg-white transition-all text-slate-800'}))
    
    BATCH_CHOICES = [
        ('2025-2026 FY', '2025-2026 FY'),
        ('2025-2026 SY', '2025-2026 SY'),
        ('2026-2027 FY', '2026-2027 FY'),
        ('2026-2027 SY', '2026-2027 SY'),
    ]
    batch = forms.ChoiceField(choices=BATCH_CHOICES, widget=forms.Select(attrs={'class': 'shadow-sm focus:ring-2 focus:ring-navy-500 focus:border-navy-500 block w-full sm:text-sm border-slate-300 rounded-lg py-2.5 px-4 font-medium bg-slate-50 focus:bg-white transition-all text-slate-800'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create the corresponding Student profile
            Student.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                batch=self.cleaned_data['batch']
            )
        return user
class FacultyRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3.5 border border-navy-200 rounded-xl bg-navy-50/30 text-navy-900 font-medium shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-burgundy-600 focus:border-burgundy-600 focus:bg-white text-sm'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3.5 border border-navy-200 rounded-xl bg-navy-50/30 text-navy-900 font-medium shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-burgundy-600 focus:border-burgundy-600 focus:bg-white text-sm'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3.5 border border-navy-200 rounded-xl bg-navy-50/30 text-navy-900 font-medium shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-burgundy-600 focus:border-burgundy-600 focus:bg-white text-sm'}))
    department = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3.5 border border-navy-200 rounded-xl bg-navy-50/30 text-navy-900 font-medium shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-burgundy-600 focus:border-burgundy-600 focus:bg-white text-sm', 'placeholder': 'e.g., Computer Science'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'faculty'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Faculty.objects.create(
                user=user,
                department=self.cleaned_data['department']
            )
        return user
