# encoding:utf-8

#------------------------------------------------------------------------
#
# libcairo
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libcairodoc',
name  = "Cairodoc lib",
description =  _("Provides a library for using Cairo to "
                        "generate documents."),
version = '1.0',
status = STABLE,
fname = 'libcairodoc.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
#load_on_reg = True
  )

#------------------------------------------------------------------------
#
# libgrampsxml
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libgrampsxml',
name  = "Grampsxml lib",
description =  _("Provides common functionality for Gramps XML "
                    "import/export."),
version = '1.0',
status = STABLE,
fname = 'libgrampsxml.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
#load_on_reg = True
  )
  
#------------------------------------------------------------------------
#
# libgrdb
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libgrdb',
name  = "grdb lib",
description =  _("Base class for ImportGrdb") ,
version = '1.0',
status = STABLE,
fname = 'libgrdb.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
#load_on_reg = True
  )

#------------------------------------------------------------------------
#
# libholiday
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libholiday',
name  = "holiday lib",
description =  _("Provides holiday information for different countries.") ,
version = '1.0',
status = STABLE,
fname = 'libholiday.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
#load_on_reg = True
  )

#------------------------------------------------------------------------
#
# llibhtmlbackend
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libhtmlbackend',
name  = "htmlbackend lib",
description =  _("Manages a HTML file implementing DocBackend.") ,
version = '1.0',
status = STABLE,
fname = 'libhtmlbackend.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
#load_on_reg = True
  )

#------------------------------------------------------------------------
#
# libhtmlconst
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libhtmlconst',
name  = "htmlconst lib",
description =  _("Common constants for html files.") ,
version = '1.0',
status = STABLE,
fname = 'libhtmlconst.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
#load_on_reg = True
  )

#------------------------------------------------------------------------
#
# libhtml
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libhtml',
name  = "html lib",
description =  _("Manages an HTML DOM tree.") ,
version = '1.0',
status = STABLE,
fname = 'libhtml.py',
authors = ["Gerald Britton"],
authors_email = ["gerald.britton@gmail.com"],
#load_on_reg = True
  )

#------------------------------------------------------------------------
#
# libmapservice
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libmapservice',
name  = "mapservice lib",
description =  _("Provides base functionality for map services.") ,
version = '1.0',
status = STABLE,
fname = 'libmapservice.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
)

#------------------------------------------------------------------------
#
# libodfbackend
#
#------------------------------------------------------------------------

register(GENERAL, 
id    = 'libodfbackend',
name  = "odfbackend lib",
description =  _("Manages an ODF file implementing DocBackend.") ,
version = '1.0',
status = STABLE,
fname = 'libodfbackend.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
)
