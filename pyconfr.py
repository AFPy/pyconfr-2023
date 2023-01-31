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
        f'{lang}/{name}.jinja2.html', page_name=name, lang=lang)


@app.route('/2023/<lang>/talks/<category>.html')
def talks(lang, category):
    talks = []
    with urlopen('https://cfp-2023.pycon.fr/schedule/xml/') as fd:
        tree = ElementTree.fromstring(fd.read().decode('utf-8'))
    for day in tree.findall('.//day'):
        for event in day.findall('.//event'):
            talk = {child.tag: child.text for child in event}
            talk['person'] = ', '.join(
                person.text for person in event.findall('.//person'))
            talk['id'] = event.attrib['id']
            talk['day'] = day.attrib['date']
            if talk['type'] != category:
                continue
            if 'description' in talk:
                talk['description'] = Markdown().convert(talk['description'])
            talks.append(talk)
    return render_template(
        f'{lang}/talks.jinja2.html', category=category, talks=talks, lang=lang)


@app.route('/2023/<lang>/full-schedule.html')
def schedule(lang):
    with urlopen('https://cfp-2023.pycon.fr/schedule/html/') as fd:
        html = fd.read().decode('utf-8')

    if lang == 'fr':
        html = (
            html
            .replace('Room', 'Salle')
            .replace('Saturday 18 February', 'Samedi 18 février')
            .replace('Sunday 19 February', 'Dimanche 19 février'))
    else:
        for minute in (0, 30):
            html = html.replace(f'12:{minute:02}', f'12:{minute:02} PM')
            for hour in range(9, 12):
                html = html.replace(
                    f'{hour:02}:{minute:02}', f'{hour:02}:{minute:02} AM')
            for hour in range(13, 19):
                html = html.replace(
                    f'{hour:02}:{minute:02}',
                    f'{hour-12:02}:{minute:02} PM')

    # Insert links in the table
    soup = BeautifulSoup(html, 'html.parser')
    conf_colors = {
        '#fe6f61': '1h',
        '#f6b36a': '30m',
        '#378899': 'workshop',
        '#fce16b': 'plenary',
    }
    for color, kind in conf_colors.items():
        for td in soup.find_all('td', attrs={'bgcolor': color}):
            title = next(td.children)
            anchor = slug(title)
            href = url_for('talks', lang=lang, category=kind, _anchor=anchor)
            link = soup.new_tag('a', href=href, target='_parent')
            title.wrap(link)

    for tag in soup.find_all(lambda tag: 'style' in tag.attrs):
        del tag.attrs['style']

    return render_template('schedule.jinja2.html', lang=lang, data=soup)


@app.route('/2023/pyconfr-2023.ics')
def calendar():
    with urlopen('https://cfp-2023.pycon.fr/schedule/ics/') as fd:
        calendar = Calendar.from_ical(fd.read())

    # Delete sprints
    calendar.subcomponents = [
        event for event in calendar.subcomponents
        if event['DTSTART'].dt.day != 16]

    return Response(calendar.to_ical(), mimetype='text/calendar')


@app.cli.command('freeze')
def freeze():
    Freezer(app).freeze()
