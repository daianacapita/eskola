from flask import Blueprint, render_template, g
from app.auth import login_required

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/student_area')
@login_required
def student_area():
    from flask import g
    from app.db import get_db
    if not g.user or g.user['papel'] != 'aluno':
        from flask import redirect, url_for, flash
        flash('Acesso restrito a alunos.')
        return redirect(url_for('index'))

    db = get_db()
    aluno_id = g.user['aluno_id']
    matriculas = db.execute(
        "SELECT * FROM Matriculas WHERE aluno_id=? AND status='ativa'",
        (aluno_id,)
    ).fetchall()

    turmas_info = []
    for m in matriculas:
        turma_id = m['turma_id']
        turma = db.execute(
            '''SELECT t.*, c.nome as curso_nome, c.descricao as curso_desc, a.ano as ano_letivo
               FROM Turmas t
               JOIN Cursos c ON c.id=t.curso_id
               JOIN AnoLectivo a ON a.id=t.ano_lectivo_id
               WHERE t.id=?''',
            (turma_id,)
        ).fetchone()
        disciplinas = db.execute(
            '''SELECT d.id, d.nome, d.descricao
               FROM TurmaDisciplinas td
               JOIN Disciplinas d ON d.id=td.disciplina_id
               WHERE td.turma_id=?''',
            (turma_id,)
        ).fetchall()
        periodo = turma['periodo']
        from app.admin import get_tempos
        tempos = get_tempos(periodo)
        slots = db.execute(
            '''SELECT h.dia_semana, h.tempo, d.nome as disciplina_nome
               FROM Horarios h
               JOIN TurmaDisciplinas td ON td.id=h.turma_disciplina_id
               JOIN Disciplinas d ON d.id=td.disciplina_id
               WHERE h.turma_id=?''',
            (turma_id,)
        ).fetchall()
        # Montar grade: [dia][tempo] = disciplina_nome
        grade = {dia: {tempo['tempo']: None for tempo in tempos} for dia in range(1, 6)}
        for slot in slots:
            grade[slot['dia_semana']][slot['tempo']] = slot['disciplina_nome']
        notas = db.execute(
            '''SELECT n.trimestre, d.nome as disciplina_nome, n.nota
               FROM NotasTrimestrais n
               JOIN TurmaDisciplinas td ON td.id=n.turma_disciplina_id
               JOIN Disciplinas d ON d.id=td.disciplina_id
               WHERE n.matricula_id=?
               ORDER BY d.nome, n.trimestre''',
            (m['id'],)
        ).fetchall()
        turmas_info.append({
            'turma': turma,
            'disciplinas': disciplinas,
            'tempos': tempos,
            'grade': grade,
            'notas': notas,
        })

    return render_template('student/student_area.html', turmas_info=turmas_info)