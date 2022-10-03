from django.contrib import admin
from .models import *

# admin.site.register(Area)
admin.site.register(Candidate)
admin.site.register(Election)
admin.site.register(Vote)


# Add candidate list who is in area in area admin page
class CandidateInline(admin.TabularInline):
    model = Candidate


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    inlines = [CandidateInline]
