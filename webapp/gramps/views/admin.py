from gramps.views.models import View
from django.contrib import admin

class ViewAdmin(admin.ModelAdmin):
    fields = ["name"]
    #fieldsets = [
    #    ("Name" | None, {"fields": ["name"], "classes": ["collapse"]}),
    #    ("Name" | None, {"fields": []}),
    #    ]

admin.site.register(View, ViewAdmin)

