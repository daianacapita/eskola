from datetime import datetime, timedelta

from flask import Blueprint, render_template, g, request, flash, redirect, url_for, session
from app.auth import login_required
from app.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')


def get_tempos(periodo):
    periodos = {
        'matinal': ('07:00', '12:30'),
        'vespertino': ('13:00', '17:30'),
        'pos_laboral': ('18:00', '22:30'),
    }

    if periodo not in periodos:
        periodo = 'matinal'

    inicio_str, fim_str = periodos[periodo]
    inicio = datetime.strptime(inicio_str, '%H:%M')
    fim = datetime.strptime(fim_str, '%H:%M')

    tempos = []
    t = inicio
    idx = 1

    while True:
        t_fim = t + timedelta(minutes=45)
        if t_fim > fim:
            break

        tempos.append(
            {
                'tempo': idx,
                'inicio': t.strftime('%H:%M'),
                'fim': t_fim.strftime('%H:%M'),
                'label': f"T{idx} ({t.strftime('%H:%M')}-{t_fim.strftime('%H:%M')})",
            }
        )

        idx += 1
        proximo_inicio = t_fim + timedelta(minutes=5)
        if proximo_inicio > fim:
            break
        t = proximo_inicio

    return tempos

@bp.route('/criar_curso', methods=['GET', 'POST'])
@login_required
def criar_curso():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        carga_horaria = request.form.get('carga_horaria')
        
        if not nome or not carga_horaria:
            flash('Nome e carga horária são obrigatórios.')
            return redirect(url_for('admin.criar_curso'))
        
        db = get_db()
        existing = db.execute('SELECT id FROM Cursos WHERE nome = ?', (nome,)).fetchone()
        if existing:
            flash('Curso já existe.')
            return redirect(url_for('admin.criar_curso'))
        
        db.execute('INSERT INTO Cursos (nome, descricao, carga_horaria) VALUES (?, ?, ?)', (nome, descricao, carga_horaria))
        db.commit()
        flash('Curso criado com sucesso.')
        return redirect(url_for('admin.criar_curso'))
    
    return render_template('admin/criar_curso.html')

@bp.route('/criar_disciplina', methods=['GET', 'POST'])
@login_required
def criar_disciplina():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    cursos = db.execute('SELECT id, nome FROM Cursos').fetchall()
    
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        ano = request.form.get('ano')
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        carga_semanal = request.form.get('carga_semanal', '1')
        
        if not curso_id or not ano or not nome:
            flash('Curso, classe e nome são obrigatórios.')
            return redirect(url_for('admin.criar_disciplina'))

        try:
            ano_int = int(ano)
        except (TypeError, ValueError):
            flash('Classe inválida.')
            return redirect(url_for('admin.criar_disciplina'))

        if ano_int < 10 or ano_int > 12:
            flash('Classe inválida.')
            return redirect(url_for('admin.criar_disciplina'))

        try:
            carga_semanal_int = int(carga_semanal)
        except (TypeError, ValueError):
            flash('Carga semanal inválida.')
            return redirect(url_for('admin.criar_disciplina'))

        if carga_semanal_int < 1 or carga_semanal_int > 15:
            flash('Carga semanal inválida. Use um valor entre 1 e 15.')
            return redirect(url_for('admin.criar_disciplina'))
        
        existing = db.execute(
            'SELECT id FROM Disciplinas WHERE curso_id = ? AND ano = ? AND nome = ?',
            (curso_id, ano_int, nome)
        ).fetchone()
        if existing:
            flash('Disciplina já existe neste curso e classe.')
            return redirect(url_for('admin.criar_disciplina'))
        
        db.execute(
            'INSERT INTO Disciplinas (curso_id, ano, nome, descricao, carga_semanal) VALUES (?, ?, ?, ?, ?)',
            (curso_id, ano_int, nome, descricao, carga_semanal_int)
        )
        db.commit()
        flash('Disciplina criada com sucesso.')
        return redirect(url_for('admin.criar_disciplina'))
    
    return render_template('admin/criar_disciplina.html', cursos=cursos)

@bp.route('/criar_turma', methods=['GET', 'POST'])
@login_required
def criar_turma():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    cursos = db.execute('SELECT id, nome FROM Cursos').fetchall()
    anos_lectivos = db.execute('SELECT id, ano FROM AnoLectivo').fetchall()
    
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        ano_lectivo_id = request.form.get('ano_lectivo_id')
        ano = request.form.get('ano')
        periodo = request.form.get('periodo')
        sala_aula = request.form.get('sala_aula')
        designacao = request.form.get('designacao')
        
        if not curso_id or not ano_lectivo_id or not ano:
            flash('Curso, ano lectivo e ano são obrigatórios.')
            return redirect(url_for('admin.criar_turma'))

        try:
            ano_int = int(ano)
        except (TypeError, ValueError):
            flash('Classe inválida. Use 10, 11 ou 12.')
            return redirect(url_for('admin.criar_turma'))

        if ano_int < 10 or ano_int > 12:
            flash('Classe inválida. Use 10, 11 ou 12.')
            return redirect(url_for('admin.criar_turma'))

        if designacao is None:
            designacao = ''

        if periodo not in ('matinal', 'vespertino', 'pos_laboral'):
            flash('Período inválido.')
            return redirect(url_for('admin.criar_turma'))
        
        existing = db.execute('SELECT id FROM Turmas WHERE curso_id = ? AND ano_lectivo_id = ? AND ano = ? AND designacao = ?', 
                              (curso_id, ano_lectivo_id, ano_int, designacao)).fetchone()
        if existing:
            flash('Turma já existe.')
            return redirect(url_for('admin.criar_turma'))
        
        db.execute(
            'INSERT INTO Turmas (curso_id, ano_lectivo_id, ano, periodo, sala_aula, designacao) VALUES (?, ?, ?, ?, ?, ?)',
            (curso_id, ano_lectivo_id, ano_int, periodo, sala_aula, designacao)
        )

        turma_id_row = db.execute('SELECT last_insert_rowid()').fetchone()
        turma_id = turma_id_row[0] if turma_id_row is not None else None

        if turma_id is not None:
            disciplinas = db.execute(
                'SELECT id FROM Disciplinas WHERE curso_id = ? AND ano = ?',
                (curso_id, ano_int)
            ).fetchall()
            if disciplinas:
                db.executemany(
                    'INSERT OR IGNORE INTO TurmaDisciplinas (turma_id, disciplina_id) VALUES (?, ?)',
                    [(turma_id, d['id']) for d in disciplinas]
                )

        db.commit()
        flash('Turma criada com sucesso.')
        return redirect(url_for('admin.criar_turma'))
    
    return render_template('admin/criar_turma.html', cursos=cursos, anos_lectivos=anos_lectivos)

@bp.route('/matricular')
@login_required
def matricular():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    alunos = db.execute('SELECT id, nome FROM Alunos').fetchall()
    turmas = db.execute('SELECT id, designacao FROM Turmas').fetchall()
    return render_template('admin/matricular.html', alunos=alunos, turmas=turmas)

@bp.route('/cursos')
@login_required
def cursos():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    cursos = db.execute('SELECT * FROM Cursos').fetchall()
    return render_template('admin/cursos.html', cursos=cursos)


@bp.route('/curso/<int:id>')
@login_required
def curso_detalhes(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    db = get_db()
    curso = db.execute('SELECT * FROM Cursos WHERE id = ?', (id,)).fetchone()
    if curso is None:
        flash('Curso não encontrado.')
        return redirect(url_for('admin.cursos'))

    turmas = db.execute(
        '''
        SELECT t.id, t.ano, t.designacao, t.sala_aula, a.ano as ano_lectivo
        FROM Turmas t
        JOIN AnoLectivo a ON t.ano_lectivo_id = a.id
        WHERE t.curso_id = ?
        ORDER BY t.ano, a.ano DESC, t.designacao
        ''',
        (id,)
    ).fetchall()

    turmas_por_classe = {}
    for turma in turmas:
        turmas_por_classe.setdefault(turma['ano'], []).append(turma)

    classes = sorted(turmas_por_classe.keys())
    return render_template(
        'admin/curso_detalhes.html',
        curso=curso,
        classes=classes,
        turmas_por_classe=turmas_por_classe
    )

@bp.route('/deletar_curso/<int:id>', methods=['POST'])
@login_required
def deletar_curso(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('DELETE FROM Cursos WHERE id = ?', (id,))
    db.commit()
    flash('Curso deletado.')
    return redirect(url_for('admin.cursos'))

@bp.route('/disciplinas')
@login_required
def disciplinas():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    disciplinas = db.execute('''
        SELECT d.*, c.nome as curso_nome 
        FROM Disciplinas d 
        JOIN Cursos c ON d.curso_id = c.id
    ''').fetchall()
    return render_template('admin/disciplinas.html', disciplinas=disciplinas)


@bp.route('/disciplina/<int:id>')
@login_required
def disciplina_detalhes(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    db = get_db()
    disciplina = db.execute(
        '''
        SELECT d.*, c.nome as curso_nome
        FROM Disciplinas d
        JOIN Cursos c ON c.id = d.curso_id
        WHERE d.id = ?
        ''',
        (id,)
    ).fetchone()

    if disciplina is None:
        flash('Disciplina não encontrada.')
        return redirect(url_for('admin.disciplinas'))

    turmas = db.execute(
        '''
        SELECT
          t.id as turma_id,
          t.designacao,
          t.ano,
          t.periodo,
          a.ano as ano_lectivo,
          p.nome as professor_nome
        FROM TurmaDisciplinas td
        JOIN Turmas t ON t.id = td.turma_id
        JOIN AnoLectivo a ON a.id = t.ano_lectivo_id
        LEFT JOIN Docencia doc ON doc.turma_disciplina_id = td.id AND doc.data_fim IS NULL
        LEFT JOIN Professores p ON p.id = doc.professor_id
        WHERE td.disciplina_id = ?
        ORDER BY a.ano DESC, t.ano, t.designacao
        ''',
        (id,)
    ).fetchall()

    carga_min = (disciplina['carga_semanal'] or 1) * 45
    hh = carga_min // 60
    mm = carga_min % 60
    carga_hhmm = f'{hh:02d}:{mm:02d}'

    return render_template(
        'admin/disciplina_detalhes.html',
        disciplina=disciplina,
        turmas=turmas,
        carga_min=carga_min,
        carga_hhmm=carga_hhmm
    )


@bp.route('/disciplina/<int:id>/atualizar_carga', methods=['POST'])
@login_required
def atualizar_carga_disciplina(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    carga_semanal = request.form.get('carga_semanal', '1')
    try:
        carga_int = int(carga_semanal)
    except (TypeError, ValueError):
        flash('Carga semanal inválida.')
        return redirect(url_for('admin.disciplina_detalhes', id=id))

    if carga_int < 1 or carga_int > 15:
        flash('Carga semanal inválida. Use um valor entre 1 e 15.')
        return redirect(url_for('admin.disciplina_detalhes', id=id))

    db = get_db()
    existe = db.execute('SELECT id FROM Disciplinas WHERE id = ?', (id,)).fetchone()
    if existe is None:
        flash('Disciplina não encontrada.')
        return redirect(url_for('admin.disciplinas'))

    db.execute('UPDATE Disciplinas SET carga_semanal = ? WHERE id = ?', (carga_int, id))
    db.commit()
    flash('Carga semanal atualizada.')
    return redirect(url_for('admin.disciplina_detalhes', id=id))

@bp.route('/deletar_disciplina/<int:id>', methods=['POST'])
@login_required
def deletar_disciplina(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('DELETE FROM Disciplinas WHERE id = ?', (id,))
    db.commit()
    flash('Disciplina deletada.')
    return redirect(url_for('admin.disciplinas'))

@bp.route('/turmas')
@login_required
def turmas():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    turmas = db.execute('''
        SELECT t.*, c.nome as curso_nome, a.ano as ano_lectivo
        FROM Turmas t 
        JOIN Cursos c ON t.curso_id = c.id
        JOIN AnoLectivo a ON t.ano_lectivo_id = a.id
        ORDER BY c.nome, t.ano, a.ano DESC, t.designacao
    ''').fetchall()

    turmas_por_curso = {}
    for turma in turmas:
        curso_id = turma['curso_id']
        if curso_id not in turmas_por_curso:
            turmas_por_curso[curso_id] = {
                'curso_id': curso_id,
                'curso_nome': turma['curso_nome'],
                'classes': {}
            }
        turmas_por_curso[curso_id]['classes'].setdefault(turma['ano'], []).append(turma)

    cursos_agrupados = []
    for curso in sorted(turmas_por_curso.values(), key=lambda x: x['curso_nome']):
        classes_ordenadas = []
        for classe in sorted(curso['classes'].keys()):
            classes_ordenadas.append({'ano': classe, 'turmas': curso['classes'][classe]})
        cursos_agrupados.append({
            'curso_id': curso['curso_id'],
            'curso_nome': curso['curso_nome'],
            'classes': classes_ordenadas
        })

    return render_template('admin/turmas.html', cursos=cursos_agrupados)

@bp.route('/turma/<int:id>')
@login_required
def turma_detalhes(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    turma = db.execute('''
        SELECT t.*, c.nome as curso_nome, c.descricao as curso_descricao, a.ano as ano_lectivo
        FROM Turmas t 
        JOIN Cursos c ON t.curso_id = c.id
        JOIN AnoLectivo a ON t.ano_lectivo_id = a.id
        WHERE t.id = ?
    ''', (id,)).fetchone()
    
    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))
    
    alunos = db.execute('''
        SELECT a.id, a.nome, a.email, m.status
        FROM Alunos a
        JOIN Matriculas m ON a.id = m.aluno_id
        WHERE m.turma_id = ? AND m.status = 'ativa'
        ORDER BY a.nome
    ''', (id,)).fetchall()
    
    disciplinas = db.execute('''
        SELECT d.nome, d.descricao
        FROM Disciplinas d
        JOIN TurmaDisciplinas td ON d.id = td.disciplina_id
        WHERE td.turma_id = ?
        ORDER BY d.nome
    ''', (id,)).fetchall()

    total_curso_row = db.execute(
        'SELECT COUNT(*) FROM Disciplinas WHERE curso_id = ? AND ano = ?',
        (turma['curso_id'], turma['ano'])
    ).fetchone()
    total_curso = total_curso_row[0] if total_curso_row is not None else 0

    total_atribuidas_row = db.execute(
        'SELECT COUNT(*) FROM TurmaDisciplinas WHERE turma_id = ?',
        (id,)
    ).fetchone()
    total_atribuidas = total_atribuidas_row[0] if total_atribuidas_row is not None else 0

    notas_trimestre_default = session.get('admin_notas_trimestre', 1)
    if notas_trimestre_default not in (1, 2, 3):
        notas_trimestre_default = 1
    
    return render_template(
        'admin/turma_detalhes.html',
        turma=turma,
        alunos=alunos,
        disciplinas=disciplinas,
        total_curso=total_curso,
        total_atribuidas=total_atribuidas,
        notas_trimestre_default=notas_trimestre_default
    )


@bp.route('/turma/<int:id>/notas')
@login_required
def notas_turma(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    trimestre = request.args.get('trimestre')
    if trimestre is None:
        trimestre_int = session.get('admin_notas_trimestre', 1)
    else:
        try:
            trimestre_int = int(trimestre)
        except (TypeError, ValueError):
            trimestre_int = 1
    if trimestre_int not in (1, 2, 3):
        trimestre_int = 1

    session['admin_notas_trimestre'] = trimestre_int

    db = get_db()
    turma = db.execute('''
        SELECT t.*, c.nome as curso_nome, c.descricao as curso_descricao, a.ano as ano_lectivo
        FROM Turmas t
        JOIN Cursos c ON t.curso_id = c.id
        JOIN AnoLectivo a ON t.ano_lectivo_id = a.id
        WHERE t.id = ?
    ''', (id,)).fetchone()

    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    matriculas = db.execute('''
        SELECT m.id as matricula_id, a.id as aluno_id, a.nome
        FROM Matriculas m
        JOIN Alunos a ON a.id = m.aluno_id
        WHERE m.turma_id = ? AND m.status = 'ativa'
        ORDER BY a.nome
    ''', (id,)).fetchall()

    turma_disciplinas = db.execute('''
        SELECT td.id as turma_disciplina_id, d.nome as disciplina_nome
        FROM TurmaDisciplinas td
        JOIN Disciplinas d ON d.id = td.disciplina_id
        WHERE td.turma_id = ?
        ORDER BY d.nome
    ''', (id,)).fetchall()

    notas_rows = db.execute('''
        SELECT nt.matricula_id, nt.turma_disciplina_id, nt.trimestre, nt.nota
        FROM NotasTrimestrais nt
        JOIN Matriculas m ON m.id = nt.matricula_id
        JOIN TurmaDisciplinas td ON td.id = nt.turma_disciplina_id
        WHERE m.turma_id = ? AND td.turma_id = ? AND nt.trimestre = ?
    ''', (id, id, trimestre_int)).fetchall()

    notas = {}
    for row in notas_rows:
        notas[(row['matricula_id'], row['turma_disciplina_id'])] = row['nota']

    total_esperado = len(matriculas) * len(turma_disciplinas)
    total_preenchido = len(notas)

    return render_template(
        'admin/notas_turma.html',
        turma=turma,
        trimestre=trimestre_int,
        matriculas=matriculas,
        turma_disciplinas=turma_disciplinas,
        notas=notas,
        total_esperado=total_esperado,
        total_preenchido=total_preenchido
    )


@bp.route('/turma/<int:id>/notas/salvar', methods=['POST'])
@login_required
def salvar_notas_turma(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    trimestre = request.form.get('trimestre')
    try:
        trimestre_int = int(trimestre)
    except (TypeError, ValueError):
        flash('Trimestre inválido.')
        return redirect(url_for('admin.notas_turma', id=id))

    if trimestre_int not in (1, 2, 3):
        flash('Trimestre inválido.')
        return redirect(url_for('admin.notas_turma', id=id))

    db = get_db()
    turma = db.execute('SELECT id FROM Turmas WHERE id = ?', (id,)).fetchone()
    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    valid_matriculas_rows = db.execute(
        "SELECT id FROM Matriculas WHERE turma_id = ? AND status = 'ativa'",
        (id,)
    ).fetchall()
    valid_matriculas = {row['id'] for row in valid_matriculas_rows}

    valid_td_rows = db.execute(
        'SELECT id FROM TurmaDisciplinas WHERE turma_id = ?',
        (id,)
    ).fetchall()
    valid_turma_disciplinas = {row['id'] for row in valid_td_rows}

    for key, value in request.form.items():
        if not key.startswith('nota-'):
            continue

        parts = key.split('-', 2)
        if len(parts) != 3:
            continue

        try:
            matricula_id = int(parts[1])
            turma_disciplina_id = int(parts[2])
        except (TypeError, ValueError):
            flash('Dados inválidos nas notas.')
            return redirect(url_for('admin.notas_turma', id=id, trimestre=trimestre_int))

        if matricula_id not in valid_matriculas or turma_disciplina_id not in valid_turma_disciplinas:
            continue

        raw = (value or '').strip()
        if raw == '':
            db.execute(
                'DELETE FROM NotasTrimestrais WHERE matricula_id = ? AND turma_disciplina_id = ? AND trimestre = ?',
                (matricula_id, turma_disciplina_id, trimestre_int)
            )
            continue

        try:
            nota = float(raw.replace(',', '.'))
        except ValueError:
            flash('Nota inválida. Use um número entre 0 e 20.')
            return redirect(url_for('admin.notas_turma', id=id, trimestre=trimestre_int))

        if nota < 0 or nota > 20:
            flash('Nota inválida. Use um número entre 0 e 20.')
            return redirect(url_for('admin.notas_turma', id=id, trimestre=trimestre_int))

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
    return redirect(url_for('admin.notas_turma', id=id, trimestre=trimestre_int))


@bp.route('/turma/<int:id>/horario')
@login_required
def horario_turma(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    db = get_db()
    turma = db.execute(
        '''
        SELECT t.*, c.nome as curso_nome, c.descricao as curso_descricao, a.ano as ano_lectivo
        FROM Turmas t
        JOIN Cursos c ON t.curso_id = c.id
        JOIN AnoLectivo a ON t.ano_lectivo_id = a.id
        WHERE t.id = ?
        ''',
        (id,)
    ).fetchone()

    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    periodo_labels = {
        'matinal': 'Matinal (07:00–12:30)',
        'vespertino': 'Vespertino (13:00–17:30)',
        'pos_laboral': 'Pós-laboral (18:00–22:30)',
    }
    periodo_label = periodo_labels.get(turma['periodo'], turma['periodo'])

    turma_disciplinas = db.execute(
        '''
        SELECT td.id as turma_disciplina_id, d.nome
        FROM TurmaDisciplinas td
        JOIN Disciplinas d ON d.id = td.disciplina_id
        WHERE td.turma_id = ?
        ORDER BY d.nome
        ''',
        (id,)
    ).fetchall()

    carga_rows = db.execute(
        '''
        SELECT td.id as turma_disciplina_id, d.carga_semanal
        FROM TurmaDisciplinas td
        JOIN Disciplinas d ON d.id = td.disciplina_id
        WHERE td.turma_id = ?
        ''',
        (id,)
    ).fetchall()
    carga_td = {row['turma_disciplina_id']: row['carga_semanal'] for row in carga_rows}

    td_nome = {row['turma_disciplina_id']: row['nome'] for row in turma_disciplinas}

    horarios_rows = db.execute(
        '''
        SELECT dia_semana, tempo, turma_disciplina_id
        FROM Horarios
        WHERE turma_id = ?
        ''',
        (id,)
    ).fetchall()

    contagens_rows = db.execute(
        'SELECT turma_disciplina_id, COUNT(*) as cnt FROM Horarios WHERE turma_id = ? GROUP BY turma_disciplina_id',
        (id,)
    ).fetchall()
    contagens_td = {row['turma_disciplina_id']: row['cnt'] for row in contagens_rows}

    slots = {}
    for row in horarios_rows:
        slots[(row['dia_semana'], row['tempo'])] = row['turma_disciplina_id']

    tempos = get_tempos(turma['periodo'])
    max_tempo = len(tempos)

    return render_template(
        'admin/horario_turma.html',
        turma=turma,
        periodo_label=periodo_label,
        tempos=tempos,
        max_tempo=max_tempo,
        turma_disciplinas=turma_disciplinas,
        slots=slots,
        td_nome=td_nome,
        contagens_td=contagens_td,
        carga_td=carga_td
    )


@bp.route('/turma/<int:id>/horario/atribuir', methods=['POST'])
@login_required
def atribuir_horario(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    dia_semana = request.form.get('dia_semana')
    tempo = request.form.get('tempo')
    turma_disciplina_id = request.form.get('turma_disciplina_id')

    if not dia_semana or not tempo or not turma_disciplina_id:
        flash('Dados inválidos.')
        return redirect(url_for('admin.horario_turma', id=id))

    try:
        dia_int = int(dia_semana)
        tempo_int = int(tempo)
        td_id_int = int(turma_disciplina_id)
    except (TypeError, ValueError):
        flash('Dados inválidos.')
        return redirect(url_for('admin.horario_turma', id=id))

    if dia_int not in (1, 2, 3, 4, 5):
        flash('Dia inválido.')
        return redirect(url_for('admin.horario_turma', id=id))

    db = get_db()
    turma = db.execute('SELECT id, periodo FROM Turmas WHERE id = ?', (id,)).fetchone()
    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    tempos = get_tempos(turma['periodo'])
    if tempo_int < 1 or tempo_int > len(tempos):
        flash('Tempo inválido para o período da turma.')
        return redirect(url_for('admin.horario_turma', id=id))

    current_slot = db.execute(
        'SELECT turma_disciplina_id FROM Horarios WHERE turma_id = ? AND dia_semana = ? AND tempo = ?',
        (id, dia_int, tempo_int)
    ).fetchone()
    if current_slot is not None and current_slot['turma_disciplina_id'] == td_id_int:
        flash('Horário atualizado.')
        return redirect(url_for('admin.horario_turma', id=id))

    td = db.execute(
        'SELECT 1 FROM TurmaDisciplinas WHERE id = ? AND turma_id = ?',
        (td_id_int, id)
    ).fetchone()
    if td is None:
        flash('Disciplina não pertence à turma.')
        return redirect(url_for('admin.horario_turma', id=id))

    carga_row = db.execute(
        '''
        SELECT d.carga_semanal
        FROM TurmaDisciplinas td
        JOIN Disciplinas d ON d.id = td.disciplina_id
        WHERE td.id = ? AND td.turma_id = ?
        ''',
        (td_id_int, id)
    ).fetchone()
    if carga_row is None:
        flash('Disciplina inválida.')
        return redirect(url_for('admin.horario_turma', id=id))

    carga_semanal = carga_row['carga_semanal']
    count_row = db.execute(
        'SELECT COUNT(*) FROM Horarios WHERE turma_id = ? AND turma_disciplina_id = ?',
        (id, td_id_int)
    ).fetchone()
    count_atual = count_row[0] if count_row is not None else 0
    novo_count = count_atual + 1
    if novo_count > carga_semanal:
        flash(f'Limite semanal atingido para esta disciplina ({carga_semanal} por semana).')
        return redirect(url_for('admin.horario_turma', id=id))

    professor_row = db.execute(
        'SELECT professor_id FROM Docencia WHERE turma_disciplina_id = ? AND data_fim IS NULL',
        (td_id_int,)
    ).fetchone()
    professor_id = professor_row['professor_id'] if professor_row is not None else None
    if professor_id is not None:
        conflito = db.execute(
            '''
            SELECT 1
            FROM Horarios h
            JOIN Docencia doc2
              ON doc2.turma_disciplina_id = h.turma_disciplina_id
             AND doc2.data_fim IS NULL
            WHERE h.dia_semana = ? AND h.tempo = ?
              AND doc2.professor_id = ?
              AND h.turma_id != ?
            LIMIT 1
            ''',
            (dia_int, tempo_int, professor_id, id)
        ).fetchone()
        if conflito is not None:
            flash('Conflito: este professor já tem aula neste dia/tempo noutra turma.')
            return redirect(url_for('admin.horario_turma', id=id))

    try:
        db.execute(
            '''
            INSERT INTO Horarios (turma_id, turma_disciplina_id, dia_semana, tempo)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(turma_id, dia_semana, tempo)
            DO UPDATE SET turma_disciplina_id = excluded.turma_disciplina_id
            ''',
            (id, td_id_int, dia_int, tempo_int)
        )
    except Exception:
        # fallback: UPDATE first, if no row updated then INSERT
        cur = db.execute(
            'UPDATE Horarios SET turma_disciplina_id = ? WHERE turma_id = ? AND dia_semana = ? AND tempo = ?',
            (td_id_int, id, dia_int, tempo_int)
        )
        if cur.rowcount == 0:
            db.execute(
                'INSERT INTO Horarios (turma_id, turma_disciplina_id, dia_semana, tempo) VALUES (?, ?, ?, ?)',
                (id, td_id_int, dia_int, tempo_int)
            )

    db.commit()
    flash('Horário atualizado.')
    return redirect(url_for('admin.horario_turma', id=id))


@bp.route('/turma/<int:id>/horario/remover', methods=['POST'])
@login_required
def remover_horario(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    dia_semana = request.form.get('dia_semana')
    tempo = request.form.get('tempo')

    try:
        dia_int = int(dia_semana)
        tempo_int = int(tempo)
    except (TypeError, ValueError):
        flash('Dados inválidos.')
        return redirect(url_for('admin.horario_turma', id=id))

    if dia_int not in (1, 2, 3, 4, 5):
        flash('Dia inválido.')
        return redirect(url_for('admin.horario_turma', id=id))

    db = get_db()
    turma = db.execute('SELECT id, periodo FROM Turmas WHERE id = ?', (id,)).fetchone()
    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    tempos = get_tempos(turma['periodo'])
    if tempo_int < 1 or tempo_int > len(tempos):
        flash('Tempo inválido para o período da turma.')
        return redirect(url_for('admin.horario_turma', id=id))

    db.execute(
        'DELETE FROM Horarios WHERE turma_id = ? AND dia_semana = ? AND tempo = ?',
        (id, dia_int, tempo_int)
    )
    db.commit()
    flash('Slot removido.')
    return redirect(url_for('admin.horario_turma', id=id))


@bp.route('/turma/<int:id>/docencia')
@login_required
def docencia_turma(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    db = get_db()
    turma = db.execute('''
        SELECT t.*, c.nome as curso_nome, c.descricao as curso_descricao, a.ano as ano_lectivo
        FROM Turmas t
        JOIN Cursos c ON t.curso_id = c.id
        JOIN AnoLectivo a ON t.ano_lectivo_id = a.id
        WHERE t.id = ?
    ''', (id,)).fetchone()

    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    turma_disciplinas = db.execute('''
        SELECT
            td.id as turma_disciplina_id,
            d.nome as disciplina_nome,
            p.id as professor_id,
            p.nome as professor_nome
        FROM TurmaDisciplinas td
        JOIN Disciplinas d ON d.id = td.disciplina_id
        LEFT JOIN Docencia doc
            ON doc.turma_disciplina_id = td.id
            AND doc.data_fim IS NULL
        LEFT JOIN Professores p
            ON p.id = doc.professor_id
        WHERE td.turma_id = ?
        ORDER BY d.nome
    ''', (id,)).fetchall()

    professores = db.execute(
        'SELECT id, nome FROM Professores ORDER BY nome'
    ).fetchall()

    total_disciplinas = len(turma_disciplinas)
    total_atribuidas = sum(1 for row in turma_disciplinas if row['professor_id'] is not None)

    return render_template(
        'admin/docencia_turma.html',
        turma=turma,
        turma_disciplinas=turma_disciplinas,
        professores=professores,
        total_disciplinas=total_disciplinas,
        total_atribuidas=total_atribuidas
    )


@bp.route('/turma/<int:id>/docencia/atribuir', methods=['POST'])
@login_required
def atribuir_docencia(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    turma_disciplina_id = request.form.get('turma_disciplina_id')
    professor_id = request.form.get('professor_id')

    if not turma_disciplina_id or not professor_id:
        flash('Selecione uma disciplina e um professor.')
        return redirect(url_for('admin.docencia_turma', id=id))

    try:
        turma_disciplina_id_int = int(turma_disciplina_id)
        professor_id_int = int(professor_id)
    except (TypeError, ValueError):
        flash('Dados inválidos.')
        return redirect(url_for('admin.docencia_turma', id=id))

    db = get_db()

    td = db.execute(
        'SELECT id FROM TurmaDisciplinas WHERE id = ? AND turma_id = ?',
        (turma_disciplina_id_int, id)
    ).fetchone()
    if td is None:
        flash('Disciplina não pertence à turma.')
        return redirect(url_for('admin.docencia_turma', id=id))

    prof = db.execute(
        'SELECT id FROM Professores WHERE id = ?',
        (professor_id_int,)
    ).fetchone()
    if prof is None:
        flash('Professor não encontrado.')
        return redirect(url_for('admin.docencia_turma', id=id))

    current = db.execute(
        'SELECT professor_id FROM Docencia WHERE turma_disciplina_id = ? AND data_fim IS NULL',
        (turma_disciplina_id_int,)
    ).fetchone()
    if current is not None and current['professor_id'] == professor_id_int:
        flash('Professor já está atribuído a esta disciplina.')
        return redirect(url_for('admin.docencia_turma', id=id))

    db.execute(
        'UPDATE Docencia SET data_fim = CURRENT_DATE WHERE turma_disciplina_id = ? AND data_fim IS NULL',
        (turma_disciplina_id_int,)
    )

    try:
        db.execute(
            'INSERT INTO Docencia (turma_disciplina_id, professor_id, data_inicio) VALUES (?, ?, CURRENT_DATE)',
            (turma_disciplina_id_int, professor_id_int)
        )
    except Exception:
        db.execute(
            "INSERT INTO Docencia (turma_disciplina_id, professor_id, data_inicio) VALUES (?, ?, datetime('now','localtime'))",
            (turma_disciplina_id_int, professor_id_int)
        )

    db.commit()
    flash('Professor atribuído com sucesso.')
    return redirect(url_for('admin.docencia_turma', id=id))


@bp.route('/turma/<int:id>/sync_disciplinas', methods=['POST'])
@login_required
def sync_disciplinas(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))

    db = get_db()
    turma = db.execute('SELECT id, curso_id, ano FROM Turmas WHERE id = ?', (id,)).fetchone()
    if turma is None:
        flash('Turma não encontrada.')
        return redirect(url_for('admin.turmas'))

    db.execute(
        '''
        INSERT OR IGNORE INTO TurmaDisciplinas (turma_id, disciplina_id)
        SELECT ?, d.id
        FROM Disciplinas d
        WHERE d.curso_id = ? AND d.ano = ?
        ''',
        (id, turma['curso_id'], turma['ano'])
    )
    db.commit()
    flash('Disciplinas sincronizadas com sucesso.')
    return redirect(url_for('admin.turma_detalhes', id=id))

@bp.route('/deletar_turma/<int:id>', methods=['POST'])
@login_required
def deletar_turma(id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('DELETE FROM Turmas WHERE id = ?', (id,))
    db.commit()
    flash('Turma deletada.')
    return redirect(url_for('admin.turmas'))

@bp.route('/aprovar_alunos')
@login_required
def aprovar_alunos():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    alunos_pendentes = db.execute('''
        SELECT u.id as user_id, a.id as aluno_id, a.nome, a.email, a.curso_preferido_id, a.ano_preferido
        FROM Usuarios u
        JOIN Alunos a ON u.aluno_id = a.id
        WHERE u.status = 'pendente' AND u.papel = 'aluno'
    ''').fetchall()
    
    # For each student, get matching turmas
    alunos_com_turmas = []
    for aluno in alunos_pendentes:
        turmas = db.execute('''
            SELECT t.id, t.designacao, c.nome as curso_nome
            FROM Turmas t
            JOIN Cursos c ON t.curso_id = c.id
            WHERE t.curso_id = ? AND t.ano = ?
        ''', (aluno['curso_preferido_id'], aluno['ano_preferido'])).fetchall()
        alunos_com_turmas.append({
            'user_id': aluno['user_id'],
            'aluno_id': aluno['aluno_id'],
            'nome': aluno['nome'],
            'email': aluno['email'],
            'turmas': turmas
        })
    
    return render_template('admin/aprovar_alunos.html', alunos=alunos_com_turmas)

@bp.route('/aprovar_aluno/<int:user_id>', methods=['POST'])
@login_required
def aprovar_aluno(user_id):
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    turma_id = request.form.get('turma_id')
    if not turma_id:
        flash('Selecione uma turma.')
        return redirect(url_for('admin.aprovar_alunos'))
    
    db = get_db()
    # Update status to ativo
    db.execute('UPDATE Usuarios SET status = ? WHERE id = ?', ('ativo', user_id))
    # Get aluno_id
    user = db.execute('SELECT aluno_id FROM Usuarios WHERE id = ?', (user_id,)).fetchone()
    if user:
        aluno_id = user['aluno_id']
        # Matricular
        existing = db.execute('SELECT id FROM Matriculas WHERE aluno_id = ? AND turma_id = ?', (aluno_id, turma_id)).fetchone()
        if not existing:
            db.execute('INSERT INTO Matriculas (aluno_id, turma_id) VALUES (?, ?)', (aluno_id, turma_id))
    db.commit()
    flash('Aluno aprovado e matriculado.')
    return redirect(url_for('admin.aprovar_alunos'))

@bp.route('/anuncios')
@login_required
def anuncios():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    db = get_db()
    anuncios = db.execute('SELECT * FROM Anuncios ORDER BY data_publicacao DESC').fetchall()
    return render_template('admin/anuncios.html', anuncios=anuncios)

@bp.route('/criar_anuncio', methods=['GET', 'POST'])
@login_required
def criar_anuncio():
    if g.user['papel'] != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        
        if not titulo or not conteudo:
            flash('Título e conteúdo são obrigatórios.')
            return redirect(url_for('admin.criar_anuncio'))
        
        db = get_db()
        db.execute('INSERT INTO Anuncios (titulo, conteudo, admin_id) VALUES (?, ?, ?)', (titulo, conteudo, g.user['id']))
        db.commit()
        flash('Anúncio criado com sucesso.')
        return redirect(url_for('admin.anuncios'))
    
    return render_template('admin/criar_anuncio.html')