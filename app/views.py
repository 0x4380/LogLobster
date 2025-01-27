from time import perf_counter

from flask import Blueprint, render_template, request, redirect
from .models import Log
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Qty of logs per page

    logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page)

    return render_template('logs.html', logs=logs)


@main.route('/http')
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    #logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page)
    logs = Log.query.filter_by(query_type='HTTP').order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('logs.html', logs=logs)


@main.route('/dns')
def get_dns_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    logs = Log.query.filter_by(query_type='DNS').order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('logs.html', logs=logs)

@main.route('/search')
def search():
    query = request.args.get('q')
    if query:
        logs = Log.query.filter(Log.query_name.like(f'%{query}%')).all()
        return render_template('logs.html', logs=logs)
    return render_template('logs.html', logs=[])

@main.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log = Log.query.get(log_id)
    if log:
        db.session.delete(log)
        db.session.commit()
    return redirect('/')

