from flask import Blueprint, render_template, g
from app.auth import login_required

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/area')
@login_required
def student_area():
    return render_template('student_area.html')