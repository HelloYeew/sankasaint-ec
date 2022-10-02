from django.contrib import admin
from .models import *

admin.site.register(Area)
admin.site.register(Candidate)
admin.site.register(Election)
admin.site.register(Vote)

# Add candidate to area admin page
class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1