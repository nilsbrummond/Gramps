#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

import Date
import RelLib

#-------------------------------------------------------------------------
#
#  Convert points to cm and back
#
#-------------------------------------------------------------------------
def pt2cm(pt):
    """
    Converts points to centimeters. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param pt: points
    @type pt: float or int
    @returns: equivalent units in centimeters
    @rtype: float
    """
    return pt/28.3465

def cm2pt(cm):
    """
    Converts centimeters to points. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param cm: centimeters
    @type cm: float or int
    @returns: equivalent units in points
    @rtype: float
    """
    return cm*182.88

def draw_pie_chart(doc, center_x, center_y, radius, data, start=0):
    """
    Draws a pie chart in the specified document. The data passed is plotted as
    a pie chart. The data should consist of the actual data. Percentages of
    each slice are determined by the routine.

    @param doc: Document to which the pie chart should be added
    @type doc: BaseDoc derived class
    @param center_x: x coordinate in centimeters where the center of the pie
       chart should be. 0 is the left hand edge of the document.
    @type center_x: float
    @param center_y: y coordinate in centimeters where the center of the pie
       chart should be. 0 is the top edge of the document
    @type center_y: float
    @param radius: radius of the pie chart. The pie charts width and height
       will be twice this value.
    @type radius: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    @param start: starting point in degrees, where the default of 0 indicates
       a start point extending from the center to right in a horizontal line.
    @type start: float
    """

    total = 0.0
    for item in data:
        total += item[1]

    for item in data:
        incr = 360.0*(item[1]/total)
        doc.draw_wedge(item[0], center_x, center_y, radius, start, start + incr)
        start += incr

def draw_legend(doc, start_x, start_y, data):
    """
    Draws a legend for a graph in the specified document. The data passed is
    used to define the legend.

    @param doc: Document to which the legend chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand corner
        of the legend is placed. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the legend
        should be. 0 is the top edge of the document
    @type start_y: float
    @param data: List of tuples containing the data to be used to create the
       legend. In order to be compatible with the graph plots, the first and
       third values of the tuple used. The format is (graphics_format, value,
       legend_description).
    @type data: list
    """
    for (format, size, legend) in data:
        gstyle = doc.get_draw_style(format)
        pstyle = gstyle.get_paragraph_style()
        size = pt2cm(doc.get_style(pstyle).get_font().get_size())
        
        doc.draw_bar(format, start_x, start_y, start_x + (2*size), start_y + size)
        doc.write_at(format, legend, start_x + (3*size), start_y - (size*0.25))
        start_y += size * 1.3
        
def draw_vertical_bar_graph(doc, format, start_x, start_y, height, width, data):
    """
    Draws a vertical bar chart in the specified document. The data passed 
    should consist of the actual data. The bars are scaled appropriately by
    the routine.

    @param doc: Document to which the bar chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand side of the
       chart should be. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the chart
    should be. 0 is the top edge of the document
    @type start_y: float
    @param height: height of the graph in centimeters
    @type height: float
    @param width: width of the graph in centimeters
    @type width: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    """
    doc.draw_line(format,start_x,start_y+height,start_x,start_y)
    doc.draw_line(format,start_x,start_y+height,start_x+width,start_y+height)

    largest = 0.0
    for item in data:
        largest = max(item[1],largest)

    scale = float(height)/float(largest)
    units = len(data)
    box_width = (float(width) / (units*3.0+1.0))*2

    bottom = float(start_y)+float(height)

    start = 0.5*box_width + start_x
    for index in range(units):
        size = float(data[index][1]) * scale
        doc.draw_bar(data[index][0],start,bottom-size,start+box_width,bottom)
        start += box_width * 1.5

def estimate_age(db, person):
    """
    Estimates the age of a person based off the birth and death
    dates of the person. A tuple containing the estimated upper
    and lower bounds of the person's age is returned. If either
    the birth or death date is missing, a (-1,-1) is returned.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person object to calculate the age of
    @type person: Person
    @returns: tuple containing the lower and upper bounds of the
       person's age, or (-1,-1) if it could not be determined.
    @rtype: tuple
    """
    bhandle = person.get_birth_handle()
    dhandle = person.get_death_handle()

    # if either of the events is not defined, return an error message
    if not bhandle or not dhandle:
        return (-1,-1)

    bdata = db.get_event_from_handle(bhandle).get_date_object()
    ddata = db.get_event_from_handle(dhandle).get_date_object()

    # if the date is not valid, return an error message
    if not bdata.get_valid() or not ddata.get_valid():
        return (-1,-1)

    # if a year is not valid, return an error message
    if not bdata.get_year_valid() or not ddata.get_year_valid():
        return (-1,-1)

    bstart = bdata.get_start_date()
    bstop  = bdata.get_stop_date()

    dstart = ddata.get_start_date()
    dstop  = ddata.get_stop_date()

    def _calc_diff(low,high):
        if (low[1],low[0]) > (high[1],high[0]):
            return high[2] - low[2] - 1
        else:
            return high[2] - low[2]

    if bstop == Date.EMPTY and dstop == Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        age = (lower, lower)
    elif bstop == Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        upper = _calc_diff(bstart,dstop)
        age = (lower,upper)
    elif dstop == Date.EMPTY:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstart)
        age = (lower,upper)
    else:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstop)
        age = (lower,upper)
    return age

def sanitize_person(db,person):
    """
    Creates a new Person instance based off the passed Person
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: source Person object that will be copied with
    privacy records removed
    @type person: Person
    @returns: 'cleansed' Person object
    @rtype: Person
    """
    new_person = RelLib.Person()
    name = person.get_primary_name()

    # copy gender
    new_person.set_gender(person.get_gender())

    # copy names if not private
    if not name.get_privacy():
        new_person.set_primary_name(name)
        new_person.set_nick_name(person.get_nick_name())
    for name in person.get_alternate_names():
        if not name.get_privacy():
            new_person.add_alternate_name(name)

    # set complete flag
    new_person.set_complete_flag(person.get_complete_flag())

    # copy birth event
    event_handle = person.get_birth_handle()
    event = db.get_event_from_handle(event_handle)
    if event and not event.get_privacy():
        new_person.set_birth_handle(event_handle)

    # copy death event
    event_handle = person.get_death_handle()
    event = db.get_event_from_handle(event_handle)
    if event and not event.get_privacy():
        new_person.set_death_handle(event_handle)

    # copy event list
    for event_handle in person.get_event_list():
        event = db.get_event_from_handle(event_handle)
        if event and not event.get_privacy():
            new_person.add_event_handle(event_handle)

    # copy address list
    for address in person.get_address_list():
        if not address.get_privacy():
            new_person.add_address(RelLib.Address(address))

    # copy attribute list
    for attribute in person.get_attribute_list():
        if not attribute.get_privacy():
            new_person.add_attribute(RelLib.Attribute(attribute))

    # copy URL list
    for url in person.get_url_list():
        if not url.get_privacy():
            new_person.add_url(url)

    # copy Media reference list
    for obj in person.get_media_list():
        new_person.add_media_reference(RelLib.MediaRef(obj))

    # copy Family reference list
    for handle in person.get_family_handle_list():
        new_person.add_family_handle(handle)

    # LDS ordinances
    ord = person.get_lds_baptism()
    if ord:
        new_person.set_lds_baptism(ord)

    ord = person.get_lds_endowment()
    if ord:
        new_person.set_lds_endowment(ord)

    ord = person.get_lds_sealing()
    if ord:
        new_person.set_lds_sealing(ord)
    
    return new_person

#-------------------------------------------------------------------------
#
#  Roman numbers
#
#-------------------------------------------------------------------------
def roman(num):
    """ Integer to Roman numeral converter for 0 < num < 4000 """
    if type(num) != int:
        return "?"
    if not 0 < num < 4000:
        return "?"
    vals = (1000, 900, 500, 400, 100,  90,  50,  40,  10,   9,   5,   4,   1)
    nums = ( 'M','CM', 'D','CD', 'C','XC', 'L','XL', 'X','IX', 'V','IV', 'I')
    retval = ""
    for i in range(len(vals)):
        amount  = int(num / vals[i])
        retval += nums[i] * amount
        num    -= vals[i] * amount
    return retval

#-------------------------------------------------------------------------
#
# Strings commonly used in reports
#
#-------------------------------------------------------------------------
def empty_notes():
    # Empty stab function for when endnotes are not needed
    return ""

def born_died_str(database,person,endnotes=None,name_object=None,person_name=None):
    """
    Composes a string describing birth and death of a person.
    
    The string is composed in the following form:
        "Such-and-such was born on-a-date in a-place, 
        and died on-a-date in a-place"
    Missing information will be omitted without loss of readability.
    Optional references may be added to birth and death events.
    Optional Name object may be used to override a person's Name instance.
    Optional string may be used to override the string representation of a name.
    
    @param database GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person instance for which the string has to be composed
    @type person: Person
    @param endnotes: Function to use for reference composition. If None
    then references will not be added
    @type endnotes: function
    @param name_object: Name instance for which the phrase is composed. If None
    then the regular primary name of the person will be used
    @type name_object: Name
    @param person_name: String to override the person's name. If None then the
    regular primary name string will be used
    @type person_name: unicode
    @returns: A composed string
    @rtype: unicode
    """

    if not endnotes:
        endnotes = empty_notes

    if not name_object:
        name_object = person.get_primary_name()

    if person_name == None:
        person_name = name_object.get_regular_name()
    elif person_name == 0:
        if person.get_gender() == RelLib.Person.male:
            person_name = _('He')
        else:
            person_name = _('She')

    birth_handle = person.get_birth_handle()
    bplace = ""
    bdate = ""
    if birth_handle:
        birth = database.get_event_from_handle(birth_handle)
        bdate = birth.get_date()
        bplace_handle = birth.get_place_handle()
        if bplace_handle:
            bplace = database.get_place_from_handle(bplace_handle).get_title()

    death_handle = person.get_death_handle()
    dplace = ""
    ddate = ""
    if death_handle:
        death = database.get_event_from_handle(death_handle)
        ddate = death.get_date()
        dplace_handle = death.get_place_handle()
        if dplace_handle:
            dplace = database.get_place_from_handle(dplace_handle).get_title()

    if person.get_gender() == RelLib.Person.male:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_endnotes' : endnotes(birth) }
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate, 'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate,
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object) }
    else:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_endnotes' : endnotes(birth) }
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate, 'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate,
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object) }
    return text

def married_str(database,person,spouse,event,endnotes=None):
    """
    Composes a string describing marriage of a person.
    
    The string is composed in the following form:
        "He/She married such-and-such on-a-date" or 
        "He/She married such-and-such in a-place", 
    Missing information will be omitted without loss of readability.
    Optional references may be added to birth and death events.
    
    @param database GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person instance whose marriage is discussed
    @type person: Person
    @param spouse: Person instance to use as a spouse
    @type spouse: Person
    @param event: Event instance of marriage 
    @type event: Event
    @param endnotes: Function to use for reference composition. If None
    then references will not be added
    @type endnotes: function
    @returns: A composed string
    @rtype: unicode
    """

    if not endnotes:
        endnotes = empty_notes

    spouse_name = spouse.get_primary_name().get_regular_name()

    date = event.get_date()
    place_handle = event.get_place_handle()
    if place_handle:
        place = database.get_place_from_handle(place_handle).get_title()
    else:
        place = ""

    text = ""
    if date and place:
        if person.get_gender() == RelLib.Person.male:
                text = _('He married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event),
                    'date' : date,
                    'place' : place}
        else:
                text = _('She married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'date' : date,
                    'endnotes' : endnotes(event),
                    'place' : place}
    elif date:
        if person.get_gender() == RelLib.Person.male:
                text = _('He married %(spouse)s %(date)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event),
                    'date' : date,}
        else:
                text = _('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event),
                    'place' : place,}
    elif place:
        if person.get_gender() == RelLib.Person.male:
                text = _('He married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event),
                    'place' : place}
        else:
                text = _('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event),
                    'place' : place}
    else:
        if person.get_gender() == RelLib.Person.male:
                text = _('He married %(spouse)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event) }
        else:
                text = _('She married %(spouse)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : endnotes(event)}
    return text

def child_str(person_gender,father_name,mother_name,dead):
    """
    Composes a string describing marriage of a person.
    
    The string is composed in the following form:
        "He/She is/was the son/daughter of father_name and mother_name"
    Missing information will be omitted without loss of readability.
    
    @param person_gender: Person.male, Person.female, or Person.unknown
    @type person: Person.male, Person.female, or Person.unknown
    @param father_name: String to use for father's name
    @type father_name: unicode
    @param mother_name: String to use for mother's name
    @type mother_name: unicode
    @param dead: Whether the person discussed is dead or not
    @type dead: bool
    @returns: A composed string
    @rtype: unicode
    """
    
    text = ""
    if person_gender == RelLib.Person.male:
        if mother_name and father_name:
            if dead:
                text = _("He was the son of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
            else:
                text = _("He is the son of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
        elif mother_name:
            if dead:
                text = _("He was the son of %(mother)s.") % {
                    'mother' : mother_name, }
            else:
                text = _("He is the son of %(mother)s.") % {
                    'mother' : mother_name, }
        elif father_name:
            if dead:
                text = _("He was the son of %(father)s.") % {
                    'father' : father_name, }
            else:
                text = _("He is the son of %(father)s.") % {
                    'father' : father_name, }
    else:
        if mother_name and father_name:
            if dead:
                text = _("She was the daughter of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
            else:
                text = _("She is the daughter of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
        elif mother_name:
            if dead:
                text = _("She was the daughter of %(mother)s.") % {
                    'mother' : mother_name, }
            else:
                text = _("She is the daughter of %(mother)s.") % {
                    'mother' : mother_name, }
        elif father_name:
            if dead:
                text = _("She was the daughter of %(father)s.") % {
                    'father' : father_name, }
            else:
                text = _("She is the daughter of %(father)s.") % {
                    'father' : father_name, }

    return text

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
if __name__ == "__main__":
    import BaseDoc
    import OpenOfficeDoc

    sheet = BaseDoc.StyleSheet()
    paper = BaseDoc.PaperStyle("Letter",27.94,21.59)
    doc = OpenOfficeDoc.OpenOfficeDoc(sheet,paper,None)

    font = BaseDoc.FontStyle()
    font.set_size(10)

    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    sheet.add_style('Normal', para)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,255,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("green",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((255,0,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("red",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,0,255))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("blue",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((255,255,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("yellow",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,0,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("black",g)


    doc.open("foo.sxw")
    doc.init()
    chart_data = [
        ('red',250,'red label'),
        ('green',35,'green label'),
        ('blue', 158, 'blue label'),
        ('yellow', 100, 'yellow label'),
        ]
    
    draw_pie_chart(doc, 4, 4, 3, chart_data)
    draw_legend(doc, 7.5, 2, chart_data)

    draw_vertical_bar_graph(doc, "black", 2, 10, 8, 12, chart_data)
    
    doc.close()
