import sys
sys.path.append("..")
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "gramps.settings"

from gramps.views.models import View

for view_name in ["People", "Events", "Family"]:
    v = View(name=view_name)
    v.save()

