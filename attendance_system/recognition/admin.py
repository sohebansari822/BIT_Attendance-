from django.contrib import admin
from .models import Person, Attendance


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_id', 'registered_at']
    search_fields = ['name', 'employee_id']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['person', 'date', 'time_in', 'confidence']
    list_filter = ['date']
    search_fields = ['person__name', 'person__employee_id']