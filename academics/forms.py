from django import forms

from .models import Course, Department, Mark, Semester, Subject


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class DepartmentForm(StyledModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class CourseForm(StyledModelForm):
    class Meta:
        model = Course
        fields = ["department", "name", "code", "duration_years"]


class SemesterForm(StyledModelForm):
    class Meta:
        model = Semester
        fields = ["course", "number", "academic_year", "starts_on", "ends_on"]
        widgets = {"starts_on": forms.DateInput(attrs={"type": "date"}), "ends_on": forms.DateInput(attrs={"type": "date"})}


class SubjectForm(StyledModelForm):
    class Meta:
        model = Subject
        fields = ["course", "semester", "name", "code", "credits", "faculty"]


class MarkForm(StyledModelForm):
    class Meta:
        model = Mark
        fields = ["student", "subject", "semester", "score"]
