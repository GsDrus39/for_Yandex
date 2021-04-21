from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user
from .auth import login_required
import datetime
from .models import Line, Ticket, Warnin
from . import db
from docxtpl import DocxTemplate

main = Blueprint('main', __name__)


def get_tickets(user_id):
    tickets = Ticket.query.filter(Ticket.user_id == user_id).all()
    res = []
    for i in tickets:
        ln = Line.query.filter(Line.id == i.line_id).first()
        try:
            res.append([f'{str(i.fio)} {str(i.flight_date)} {ln.from_} - {ln.to_} {ln.time}', i.id])
        except AttributeError:
            pass
    return res


@main.route('/')
def index():
    try:
        return render_template('index.html', role=current_user.urole)
    except AttributeError:
        return render_template('index.html')


@main.route('/print')
@login_required()
def print_():
    if request.method == 'GET':
        doc = DocxTemplate("app/tmpl.docx")
        id_ = request.args.get('print')
        ticket = Ticket.query.filter(Ticket.id == id_).first()
        line = Line.query.filter(Line.id == ticket.line_id).first()
        context = {
            'line_id': ticket.id,
            'from': line.from_,
            'to': line.to_,
            'date': ticket.flight_date,
            'time': line.time,
            'fio': ticket.fio,
            'class': ticket.class_
        }
        doc.render(context)
        doc.save('app/static/res.docx')
        return '<a href="static/res.docx" download="">Скачать</a>'


@main.route('/profile', methods=['GET', 'POST'])
@login_required()
def profile():
    if request.method == 'GET':
        warnins = Warnin.query.filter(Warnin.user_id == current_user.id).all()
        warnings = []
        for i in warnins:
            warnings.append(i.text)

        return render_template('profile.html', role=current_user.urole,
                               warnings=warnings, tickets=get_tickets(current_user.id))
    elif request.method == 'POST':
        Warnin.query.filter(Warnin.id == request.form.get('gotit')).delete()
        db.session.commit()
        warnins = Warnin.query.filter(Warnin.user_id == current_user.id).all()
        warnings = []
        for i in warnins:
            warnings.append([i.text, i.id])
        return render_template('profile.html', role=current_user.urole,
                               warnings=warnings, tickets=get_tickets(current_user.id))


@main.route('/creation_menu')
@login_required(role='admin')
def creation():
    return render_template('creation_menu.html', name=current_user.name, role=current_user.urole)


@main.route('/creation_menu/create', methods=['GET', 'POST'])
@login_required(role='admin')
def create():
    if request.method == 'GET':
        return render_template('create.html', name=current_user.name, role=current_user.urole)
    elif request.method == 'POST':
        from_ = request.form.get('from')
        to_ = request.form.get('to')
        time = request.form.get('time')
        plb = request.form.get('bui')
        pplb = request.form.get('buip')
        ple = request.form.get('eco')
        pple = request.form.get('ecop')
        if not all([from_, to_, time, plb, pplb, ple, pple]):
            flash('Заполните ВСЕ поля.')
            return redirect(url_for('main.create'))
        a = time.split(':')
        time = datetime.time(int(a[0]), int(a[1]))
        line = Line(time=time, seats=f'{plb}, {ple}',
                    prices=f'{pplb}, {pple}',
                    from_=from_, to_=to_)
        db.session.add(line)
        db.session.commit()
        warnins = Warnin.query.filter(Warnin.user_id == current_user.id).all()
        warnings = []
        for i in warnins:
            warnings.append(i.text)
        return redirect(url_for('main.profile'))


@main.route('/creation_menu/delete', methods=['GET', 'POST'])
@login_required(role='admin')
def delete():
    if request.method == 'GET':
        res = []
        lines = Line.query.all()
        for line in lines:
            res.append({'id': line.id, 'from_': line.from_,
                        'to_': line.to_, 'time': line.time})
        return render_template('delete.html', name=current_user.name, role=current_user.urole, lst=res)
    elif request.method == 'POST':
        ln = Line.query.filter(Line.id == request.form.get('lines')).first()
        users = Ticket.query.filter(Ticket.line_id == request.form.get('lines')).all()
        for i in users:
            a = f'Рейс {ln.from_} - {ln.to_};' \
                f' {i.flight_date} {ln.time} отменен или перенесен. Перезакажите и перепечатайте билет'
            warnin = Warnin(user_id=i.user_id, text=a)
            db.session.add(warnin)
        Line.query.filter(Line.id == request.form.get('lines')).delete()
        db.session.commit()
        return redirect(url_for('main.profile'))


@main.route('/creation_menu/modify', methods=['GET', 'POST', 'PUT'])
@login_required(role='admin')
def modify():
    if request.method == 'GET':
        res = []
        lines = Line.query.all()
        for line in lines:
            res.append({'id': line.id, 'from_': line.from_,
                        'to_': line.to_, 'time': line.time})
        return render_template('modify.html', name=current_user.name, lst1=res, role=current_user.urole, trigger=False)
    elif request.method == 'POST' and request.form.get('act'):
        lst = []
        id_ = request.form.get('lines')
        a = Line.query.filter(Line.id == id_).all()[0]
        lst += [a.time, a.from_, a.to_,
                int(a.seats.split(', ')[1]), int(a.prices.split(', ')[1]),
                int(a.seats.split(', ')[0]), int(a.prices.split(', ')[0]),
                id_]
        return render_template('modify.html', name=current_user.name, lst=lst, role=current_user.urole, trigger=True)
    elif request.method == 'POST':
        id_ = request.form.get('id')
        from_ = request.form.get('from')
        to_ = request.form.get('to')
        time = request.form.get('time')
        plb = request.form.get('bui')
        pplb = request.form.get('buip')
        ple = request.form.get('eco')
        pple = request.form.get('ecop')
        if not all([from_, to_, time, plb, pplb, ple, pple]):
            flash('Заполните ВСЕ поля.')
            return redirect(url_for('main.create'))
        a = time.split(':')
        time = datetime.time(int(a[0]), int(a[1]))
        line = Line(id=id_, time=time, seats=f'{plb}, {ple}',
                    prices=f'{pplb}, {pple}',
                    from_=from_, to_=to_)
        ln = Line.query.filter(Line.id == id_).first()
        users = Ticket.query.filter(Ticket.line_id == id_).all()
        for i in users:
            a = f'Рейс {ln.from_} - {ln.to_};' \
                f' {i.flight_date} {ln.time} отменен или перенесен. Перезакажите и перепечатайте билет'
            warnin = Warnin(user_id=i.user_id, text=a)
            db.session.add(warnin)
        Line.query.filter(Line.id == id_).delete()
        db.session.add(line)
        db.session.commit()
        return redirect(url_for('main.profile'))


@main.route('/booking', methods=['GET', 'POST'])
@login_required(role='user')
def booking():
    if request.method == 'GET':
        res = []
        lines = Line.query.all()
        for line in lines:
            res.append({'id': line.id, 'from_': line.from_,
                        'to_': line.to_, 'time': line.time})
        return render_template('booking.html', name=current_user.name, role=current_user.urole, lst=res)
    elif request.method == 'POST':
        fio = request.form.get('FIO')
        line_id = request.form.get('fromto')
        date = request.form.get('date')
        class_ = request.form.get('class')
        if len(fio.split()) != 3:
            flash('Проверьте ФИО.')
            return redirect(url_for('main.booking'))
        if not all([fio, line_id, date, class_]):
            flash('Заполните ВСЕ поля.')
            return redirect(url_for('main.booking'))
        date = date.split('-')
        if datetime.datetime.today().date() > datetime.datetime(int(date[0]), int(date[1]), int(date[2])).date():
            flash('Введите реальную дату.')
            return redirect(url_for('main.booking'))
        tickets = Ticket.query.filter(Ticket.flight_date == datetime.datetime(int(date[0]),
                                                                              int(date[1]),
                                                                              int(date[2])).date(),
                                      Ticket.line_id == line_id).all()
        seats = Line.query.filter(Line.id == line_id).all()[0].seats
        b, e = list(map(int, seats.split(', ')))
        for t in tickets:
            if t.class_ == 'bui':
                b -= 1
            else:
                e -= 1
        if class_ == 'bui' and b == 0:
            flash('Билетов нет, выберите другой класс или рейс.')
            return redirect(url_for('main.booking'))
        if class_ == 'eco' and e == 0:
            flash('Билетов нет, выберите другой класс или рейс.')
            return redirect(url_for('main.booking'))
        ticket = Ticket(flight_date=datetime.datetime(int(date[0]), int(date[1]), int(date[2])).date(),
                        fio=fio, class_=class_, line_id=line_id, user_id=current_user.id)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('main.profile'))
