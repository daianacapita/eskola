from flask import Blueprint, render_template, g, request, flash, redirect, url_for
from app.auth import login_required
from app.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

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
        
        existing = db.execute(
            'SELECT id FROM Disciplinas WHERE curso_id = ? AND ano = ? AND nome = ?',
            (curso_id, ano_int, nome)
        ).fetchone()
        if existing:
            flash('Disciplina já existe neste curso e classe.')
            return redirect(url_for('admin.criar_disciplina'))
        
        db.execute(
            'INSERT INTO Disciplinas (curso_id, ano, nome, descricao) VALUES (?, ?, ?, ?)',
            (curso_id, ano_int, nome, descricao)
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
        
        existing = db.execute('SELECT id FROM Turmas WHERE curso_id = ? AND ano_lectivo_id = ? AND ano = ? AND designacao = ?', 
                              (curso_id, ano_lectivo_id, ano_int, designacao)).fetchone()
        if existing:
            flash('Turma já existe.')
            return redirect(url_for('admin.criar_turma'))
        
        db.execute('INSERT INTO Turmas (curso_id, ano_lectivo_id, ano, sala_aula, designacao) VALUES (?, ?, ?, ?, ?)', 
                   (curso_id, ano_lectivo_id, ano_int, sala_aula, designacao))

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
    
    return render_template(
        'admin/turma_detalhes.html',
        turma=turma,
        alunos=alunos,
        disciplinas=disciplinas,
        total_curso=total_curso,
        total_atribuidas=total_atribuidas
    )


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