import sys
sys.path.append("..")
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "gramps.settings"

from gramps.views.models import View

for name,constr in [("Person", "Person", ), 
                    ("Event", "Event", ),
                    ("Family", "Family", ),
                    ("Place", "Place", ),
                    ("Source", "Source", ),
                    ("Media", "MediaObject", ),
                    ("Repository", "Repository", ),
                    ("Note", "Note", ),
                    ]:
    v = View(name=name, constructor=constr)
    v.save()
