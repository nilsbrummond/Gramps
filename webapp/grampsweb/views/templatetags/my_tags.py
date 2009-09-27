from django import template

register = template.Library()

def currentSection(view1, view2):
    if view1.strip().lower() == view2.strip().lower():
        return "CurrentSection"
    return "OtherSection"
currentSection.is_safe = True
register.filter('currentSection', currentSection)

def mult(value1, value2):
    return value1 * value2

register.filter('mult', mult)

def row_count(row, page):
    return row + (page.number - 1) * page.paginator.per_page

register.filter('row_count', row_count)

def table_header(context, headers = None):
    # add things for the header here
    if headers:
        context["headers"] = headers
    return context

register.inclusion_tag('table_header.html', 
                       takes_context=True)(table_header)

def view_navigation(context):
    # add things for the view here
    return context

register.inclusion_tag('view_navigation.html', 
                       takes_context=True)(view_navigation)

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
## Alternative page_numbers:
    page_numbers = range(max(0, context['page']-adjacent_pages), 
                         min(context['pages'], 
                             context['page']+adjacent_pages)+1) 
    results_this_page = context['object_list'].__len__()
    range_base = ((context['page'] - 1) * context['results_per_page'])

# # Original
# #    page_numbers = [n for n in range(context['page'] - adjacent_pages, 
# #                                     context['page'] + adjacent_pages + 1) 
# #                    if n > 0 and n <= context['pages']]

    return {
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'results_this_page': results_this_page,
        'first_this_page': range_base + 1,
        'last_this_page': range_base + results_this_page,
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
    }

register.inclusion_tag('paginator.html', 
                       takes_context=True)(paginator)
