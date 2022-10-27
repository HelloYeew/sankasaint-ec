from django.contrib import admin
from .models import *

# admin.site.register(Area)
admin.site.register(LegacyCandidate)
admin.site.register(LegacyElection)
admin.site.register(LegacyVote)
admin.site.register(LegacyParty)


# Add candidate list who is in area in area admin page
class CandidateInline(admin.TabularInline):
    model = LegacyCandidate


@admin.register(LegacyArea)
class AreaAdmin(admin.ModelAdmin):
    inlines = [CandidateInline]
