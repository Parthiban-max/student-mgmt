from django import forms

from academics.models import Subject
from students.models import Student
from .models import Attendance


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "subject", "date", "status", "remarks"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.TextInput(attrs={"placeholder": "Optional note"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        if user and not user.is_superuser and user.role == "FACULTY":
            self.fields["subject"].queryset = Subject.objects.filter(faculty__user=user)
        subject_id = self.data.get("subject") or getattr(self.instance, "subject_id", None)
        if subject_id:
            subject = Subject.objects.filter(pk=subject_id).first()
            if subject:
                self.fields["student"].queryset = Student.objects.filter(course=subject.course)

    def clean(self):
        cleaned = super().clean()
        student, subject = cleaned.get("student"), cleaned.get("subject")
        if student and subject and student.course_id != subject.course_id:
            self.add_error("student", "Select a student enrolled in the subject's course.")
        return cleaned
