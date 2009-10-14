from gen.web.views.models import View
from django.contrib import admin

class ViewAdmin(admin.ModelAdmin):
    fields = ["name", "constructor"]
    #fieldsets = [
    #    ("Name" | None, {"fields": ["name"], "classes": ["collapse"]}),
    #    ("Name" | None, {"fields": []}),
    #    ]

admin.site.register(View, ViewAdmin)

