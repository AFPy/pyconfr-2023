from urllib.request import urlopen
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from flask import Flask, Response, render_template, url_for
from flask_frozen import Freezer
from icalendar import Calendar
from markdown2 import Markdown
from sassutils.wsgi import SassMiddleware
from slugify import slugify

app = Flask(__name__, static_url_path='/2023/static')
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'pyconfr': {
        'sass_path': 'static/sass',
        'css_path': 'static/css',
        'wsgi_path': '/2023/static/css',
        'strip_extension': True}})


@app.template_filter()
def slug(string):
    return slugify(string, max_length=30)


@app.route('/')
@app.route('/2023/')
@app.route('/2023/<lang>/<name>.html')
def page(name='index', lang='fr'):
    return render_template(
        '{lang}/{name}.html.jinja2'.format(name=name, lang=lang),
        page_name=name, lang=lang)


# @app.route('/2023/<lang>/talks/<category>.html')
# def talks(lang, category):
#     talks = []
#     with urlopen('https://cfp-2023.pycon.fr/schedule/xml/') as fd:
#         tree = ElementTree.fromstring(fd.read().decode('utf-8'))
#     for day in tree.findall('.//day'):
#         for event in day.findall('.//event'):
#             talk = {child.tag: child.text for child in event}
#             talk['person'] = ', '.join(
#                 person.text for person in event.findall('.//person'))
#             talk['id'] = event.attrib['id']
#             talk['day'] = day.attrib['date']
#             if talk['type'] != category:
#                 continue
#             if 'description' in talk:
#                 talk['description'] = Markdown().convert(talk['description'])
#             talks.append(talk)
#     return render_template(
#         '{lang}/talks.html.jinja2'.format(lang=lang),
#         category=category, talks=talks, lang=lang)


# @app.route('/2023/<lang>/full-schedule.html')
# def schedule(lang):
#     with urlopen('https://cfp-2023.pycon.fr/schedule/html/') as fd:
#         html = fd.read().decode('utf-8')

#     if lang == 'fr':
#         html = html.replace('Room', 'Salle')
#     else:
#         html = (
#             html
#             .replace('samedi 18 février', 'Saturday, February 18')
#             .replace('dimanche 19 février', 'Sunday, February 19'))
#         for minute in (0, 30):
#             html = html.replace(f'12:{minute:02}', f'12:{minute:02} PM')
#             for hour in range(9, 12):
#                 html = html.replace(
#                     f'{hour:02}:{minute:02}', f'{hour:02}:{minute:02} AM')
#             for hour in range(13, 19):
#                 html = html.replace(
#                     f'{hour:02}:{minute:02}',
#                     f'{hour-12:02}:{minute:02} PM')

#     # Delete extra cells for sprints
#     html = (
#         html
#         .replace('colspan="9"', '')
#         .replace('<td colspan="8"></td>', ''))

#     # Insert links in the table
#     soup = BeautifulSoup(html, 'html.parser')
#     conf_colors = {
#         '#ff7373': 'keynote',
#         '#73cbef': 'workshop',
#         '#e9b96e': 'conference',
#     }
#     for color, kind in conf_colors.items():
#         for td in soup.find_all('td', attrs={'bgcolor': color}):
#             title = list(td.children)[0]
#             url = url_for('talks', lang=lang, category=kind)
#             href = f'{url}#{slug(title)}'
#             link = soup.new_tag('a', href=href, target='_parent')
#             title.wrap(link)

#     return render_template('schedule.html.jinja2', data=soup)


# @app.route('/2023/pyconfr-2023.ics')
# def calendar():
#     with urlopen('https://cfp-2023.pycon.fr/schedule/ics/') as fd:
#         calendar = Calendar.from_ical(fd.read())
#     # Delete sprints
#     calendar.subcomponents = [
#         event for event in calendar.subcomponents
#         if event['DTSTART'].dt.day != 31]
#     return Response(calendar.to_ical(), mimetype='text/calendar')


@app.cli.command('freeze')
def freeze():
    Freezer(app).freeze()
