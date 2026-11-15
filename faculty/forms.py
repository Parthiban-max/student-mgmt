from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from academics.models import Department
from .models import Faculty

User = get_user_model()


class FacultyForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    faculty_id = forms.CharField(max_length=20)
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    designation = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20, required=False)
    joined_on = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already in use.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("That email address is already in use.")
        return email

    def clean_faculty_id(self):
        faculty_id = self.cleaned_data["faculty_id"]
        if Faculty.objects.filter(faculty_id=faculty_id).exists():
            raise forms.ValidationError("That faculty ID is already in use.")
        return faculty_id

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password, User(
            username=self.cleaned_data.get("username", ""),
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
            email=self.cleaned_data.get("email", ""),
        ))
        return password

    @transaction.atomic
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            role=User.Role.FACULTY,
        )
        return Faculty.objects.create(
            user=user,
            faculty_id=self.cleaned_data["faculty_id"],
            department=self.cleaned_data["department"],
            designation=self.cleaned_data["designation"],
            phone=self.cleaned_data["phone"],
            joined_on=self.cleaned_data["joined_on"],
        )


class FacultyUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = Faculty
        fields = ["faculty_id", "department", "designation", "phone", "joined_on"]
        widgets = {"joined_on": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.fields["email"].initial = self.instance.user.email
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.user_id).exists():
            raise forms.ValidationError("That email address is already in use.")
        return email

    def clean_faculty_id(self):
        faculty_id = self.cleaned_data["faculty_id"]
        if Faculty.objects.filter(faculty_id=faculty_id).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("That faculty ID is already in use.")
        return faculty_id

    def save(self, commit=True):
        faculty = super().save(commit=False)
        faculty.user.first_name = self.cleaned_data["first_name"]
        faculty.user.last_name = self.cleaned_data["last_name"]
        faculty.user.email = self.cleaned_data["email"]
        if commit:
            faculty.user.save()
            faculty.save()
        return faculty
