from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user
from .auth import login_required
import datetime
from .models import Line
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    try:
        return render_template('index.html', role=current_user.urole)
    except AttributeError:
        return render_template('index.html')


@main.route('/profile')
@login_required()
def profile():
    return render_template('profile.html', name=current_user.name, role=current_user.urole)


@main.route('/creation_menu')
@login_required(role='admin')
def creation():
    return render_template('creation_menu.html', name=current_user.name, role=current_user.urole)


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
    elif request.method == 'POST':  # TODO перекидывание заказавших на другой рейс и уведомление об этом
        Line.query.filter(Line.id == request.form.get('lines')).delete()
        db.session.commit()
        return render_template('creation_menu.html', success=True, name=current_user.name, role=current_user.urole)


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
            flash('Please fill ALL fields and try again.')
            return redirect(url_for('main.create'))
        a = time.split(':')
        time = datetime.time(int(a[0]), int(a[1]))
        line = Line(time=time, seats=f'{plb}, {ple}',
                    prices=f'{pplb}, {pple}',
                    from_=from_, to_=to_)
        db.session.add(line)
        db.session.commit()
        return render_template('creation_menu.html', success=True, name=current_user.name, role=current_user.urole)


@main.route('/creation_menu/modify')
@login_required(role='admin')
def modify():
    return 'modify'


@main.route('/booking', methods=['GET', 'POST'])
@login_required(role='user')
def booking():
    if request.method == 'GET':
        return render_template('booking.html', name=current_user.name, role=current_user.urole)
    elif request.method == 'POST':
        fio = request.form.get('FIO')  # TODO Валидация фио; выбор пунктов назначения из списков
        from_ = request.form.get('from')
        to_ = request.form.get('to')
        date = request.form.get('date')
        class_ = request.form.get('class')
        if not all([fio, from_, to_, date, class_]):
            flash('Please fill ALL fields and try again.')
            return redirect(url_for('main.booking'))
        date = date.split('-')
        if datetime.datetime.today().date() > datetime.datetime(int(date[0]), int(date[1]), int(date[2])).date():
            flash('Please check your date and try again.')
            return redirect(url_for('main.booking'))
        return 'Done'  # TODO сопсна сам заказ
