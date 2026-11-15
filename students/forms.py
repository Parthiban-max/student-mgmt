from django import forms

from academics.models import Course
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name", "last_name", "email", "phone", "date_of_birth", "gender",
            "department", "course", "year", "enrolled_on", "address", "guardian_name", "guardian_phone",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "enrolled_on": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        if self.data.get("department"):
            self.fields["course"].queryset = Course.objects.filter(department_id=self.data["department"])
        elif self.instance.pk:
            self.fields["course"].queryset = Course.objects.filter(department=self.instance.department)

    def clean(self):
        cleaned = super().clean()
        department, course = cleaned.get("department"), cleaned.get("course")
        if department and course and course.department_id != department.id:
            self.add_error("course", "Select a course in the chosen department.")
        if course and cleaned.get("year") and cleaned["year"] > course.duration_years:
            self.add_error("year", "Year cannot exceed the course duration.")
        return cleaned
