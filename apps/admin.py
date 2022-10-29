from django.contrib import admin
from .models import *

# admin.site.register(LegacyArea)
admin.site.register(LegacyCandidate)
admin.site.register(LegacyElection)
admin.site.register(LegacyVote)
admin.site.register(LegacyParty)
admin.site.register(NewArea)
admin.site.register(NewCandidate)
admin.site.register(NewElection)
admin.site.register(VoteCheck)
admin.site.register(VoteResultParty)
admin.site.register(VoteResultCandidate)
admin.site.register(NewParty)


# Add candidate list who is in area admin page
class CandidateInline(admin.TabularInline):
    model = LegacyCandidate


@admin.register(LegacyArea)
class AreaAdmin(admin.ModelAdmin):
    inlines = [CandidateInline]
