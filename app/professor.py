import functools

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.db import get_db

bp = Blueprint('professor', __name__, url_prefix='/professor')


def professor_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        try:
            papel = g.user['papel']
            professor_id = g.user['professor_id']
        except Exception:
            flash('Acesso negado.')
            return redirect(url_for('index'))

        if papel != 'professor' or professor_id is None:
            flash('Acesso negado.')
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/')
@professor_required
def index():
    db = get_db()
    docencias = db.execute(
        '''
        SELECT
            td.id as turma_disciplina_id,
            t.id as turma_id,
            t.designacao,
            t.ano,
            c.nome as curso_nome,
            d.nome as disciplina_nome,
            a.ano as ano_lectivo
        FROM Docencia doc
        JOIN TurmaDisciplinas td ON td.id = doc.turma_disciplina_id
        JOIN Turmas t ON t.id = td.turma_id
        JOIN Cursos c ON c.id = t.curso_id
        JOIN Disciplinas d ON d.id = td.disciplina_id
        JOIN AnoLectivo a ON a.id = t.ano_lectivo_id
        WHERE doc.professor_id = ? AND doc.data_fim IS NULL
        ORDER BY a.ano DESC, c.nome, t.ano, t.designacao, d.nome
        ''',
        (g.user['professor_id'],)
    ).fetchall()

    return render_template('professor/index.html', docencias=docencias)


@bp.route('/turma_disciplina/<int:turma_disciplina_id>/notas')
@professor_required
def notas_disciplina(turma_disciplina_id):
    trimestre = request.args.get('trimestre', '1')
    try:
        trimestre_int = int(trimestre)
    except (TypeError, ValueError):
        trimestre_int = 1
    if trimestre_int not in (1, 2, 3):
        trimestre_int = 1

    db = get_db()

    contexto = db.execute(
        '''
        SELECT
            td.id as turma_disciplina_id,
            t.id as turma_id,
            t.designacao,
            t.ano,
            c.nome as curso_nome,
            d.nome as disciplina_nome,
            a.ano as ano_lectivo
        FROM Docencia doc
        JOIN TurmaDisciplinas td ON td.id = doc.turma_disciplina_id
        JOIN Turmas t ON t.id = td.turma_id
        JOIN Cursos c ON c.id = t.curso_id
        JOIN Disciplinas d ON d.id = td.disciplina_id
        JOIN AnoLectivo a ON a.id = t.ano_lectivo_id
        WHERE doc.professor_id = ? AND doc.data_fim IS NULL AND td.id = ?
        ''',
        (g.user['professor_id'], turma_disciplina_id)
    ).fetchone()

    if contexto is None:
        flash('Acesso negado.')
        return redirect(url_for('professor.index'))

    matriculas = db.execute(
        '''
        SELECT m.id as matricula_id, a.nome
        FROM Matriculas m
        JOIN Alunos a ON a.id = m.aluno_id
        WHERE m.turma_id = ? AND m.status = 'ativa'
        ORDER BY a.nome
        ''',
        (contexto['turma_id'],)
    ).fetchall()

    notas_rows = db.execute(
        '''
        SELECT matricula_id, nota
        FROM NotasTrimestrais
        WHERE turma_disciplina_id = ? AND trimestre = ?
        ''',
        (turma_disciplina_id, trimestre_int)
    ).fetchall()

    notas = {row['matricula_id']: row['nota'] for row in notas_rows}

    total_esperado = len(matriculas)
    total_preenchido = len(notas)

    return render_template(
        'professor/notas_disciplina.html',
        contexto=contexto,
        trimestre=trimestre_int,
        matriculas=matriculas,
        notas=notas,
        total_esperado=total_esperado,
        total_preenchido=total_preenchido
    )


@bp.route('/turma_disciplina/<int:turma_disciplina_id>/notas/salvar', methods=['POST'])
@professor_required
def salvar_notas_disciplina(turma_disciplina_id):
    trimestre = request.form.get('trimestre')
    try:
        trimestre_int = int(trimestre)
    except (TypeError, ValueError):
        flash('Trimestre inválido.')
        return redirect(url_for('professor.notas_disciplina', turma_disciplina_id=turma_disciplina_id))

    if trimestre_int not in (1, 2, 3):
        flash('Trimestre inválido.')
        return redirect(url_for('professor.notas_disciplina', turma_disciplina_id=turma_disciplina_id))

    db = get_db()

    contexto = db.execute(
        '''
        SELECT
            td.id as turma_disciplina_id,
            t.id as turma_id
        FROM Docencia doc
        JOIN TurmaDisciplinas td ON td.id = doc.turma_disciplina_id
        JOIN Turmas t ON t.id = td.turma_id
        WHERE doc.professor_id = ? AND doc.data_fim IS NULL AND td.id = ?
        ''',
        (g.user['professor_id'], turma_disciplina_id)
    ).fetchone()

    if contexto is None:
        flash('Acesso negado.')
        return redirect(url_for('professor.index'))

    valid_matriculas_rows = db.execute(
        "SELECT id FROM Matriculas WHERE turma_id = ? AND status = 'ativa'",
        (contexto['turma_id'],)
    ).fetchall()
    valid_matriculas = {row['id'] for row in valid_matriculas_rows}

    for key, value in request.form.items():
        if not key.startswith('nota-'):
            continue

        raw = (value or '').strip()
        if raw == '':
            continue

        parts = key.split('-', 1)
        if len(parts) != 2:
            continue

        try:
            matricula_id = int(parts[1])
        except (TypeError, ValueError):
            flash('Dados inválidos nas notas.')
            return redirect(url_for('professor.notas_disciplina', turma_disciplina_id=turma_disciplina_id, trimestre=trimestre_int))

        if matricula_id not in valid_matriculas:
            continue

        try:
            nota = float(raw.replace(',', '.'))
        except ValueError:
            flash('Nota inválida. Use um número entre 0 e 20.')
            return redirect(url_for('professor.notas_disciplina', turma_disciplina_id=turma_disciplina_id, trimestre=trimestre_int))

        if nota < 0 or nota > 20:
            flash('Nota inválida. Use um número entre 0 e 20.')
            return redirect(url_for('professor.notas_disciplina', turma_disciplina_id=turma_disciplina_id, trimestre=trimestre_int))

        try:
            db.execute(
                '''
                INSERT INTO NotasTrimestrais (matricula_id, turma_disciplina_id, trimestre, nota)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(matricula_id, turma_disciplina_id, trimestre)
                DO UPDATE SET nota = excluded.nota
                ''',
                (matricula_id, turma_disciplina_id, trimestre_int, nota)
            )
        except Exception:
            try:
                db.execute(
                    'INSERT INTO NotasTrimestrais (matricula_id, turma_disciplina_id, trimestre, nota) VALUES (?, ?, ?, ?)',
                    (matricula_id, turma_disciplina_id, trimestre_int, nota)
                )
            except Exception:
                db.execute(
                    'UPDATE NotasTrimestrais SET nota = ? WHERE matricula_id = ? AND turma_disciplina_id = ? AND trimestre = ?',
                    (nota, matricula_id, turma_disciplina_id, trimestre_int)
                )

    db.commit()
    flash(f'Notas do {trimestre_int}º trimestre salvas com sucesso.')
    return redirect(url_for('professor.notas_disciplina', turma_disciplina_id=turma_disciplina_id, trimestre=trimestre_int))
