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
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        
        if not curso_id or not nome:
            flash('Curso e nome são obrigatórios.')
            return redirect(url_for('admin.criar_disciplina'))
        
        existing = db.execute('SELECT id FROM Disciplinas WHERE curso_id = ? AND nome = ?', (curso_id, nome)).fetchone()
        if existing:
            flash('Disciplina já existe neste curso.')
            return redirect(url_for('admin.criar_disciplina'))
        
        db.execute('INSERT INTO Disciplinas (curso_id, nome, descricao) VALUES (?, ?, ?)', (curso_id, nome, descricao))
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
        
        existing = db.execute('SELECT id FROM Turmas WHERE curso_id = ? AND ano_lectivo_id = ? AND ano = ? AND designacao = ?', 
                              (curso_id, ano_lectivo_id, ano, designacao)).fetchone()
        if existing:
            flash('Turma já existe.')
            return redirect(url_for('admin.criar_turma'))
        
        db.execute('INSERT INTO Turmas (curso_id, ano_lectivo_id, ano, sala_aula, designacao) VALUES (?, ?, ?, ?, ?)', 
                   (curso_id, ano_lectivo_id, ano, sala_aula, designacao))
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
    ''').fetchall()
    return render_template('admin/turmas.html', turmas=turmas)

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
        SELECT u.id as user_id, a.id as aluno_id, a.nome, a.email
        FROM Usuarios u
        JOIN Alunos a ON u.aluno_id = a.id
        WHERE u.status = 'pendente' AND u.papel = 'aluno'
    ''').fetchall()
    turmas = db.execute('SELECT id, designacao FROM Turmas').fetchall()
    return render_template('admin/aprovar_alunos.html', alunos=alunos_pendentes, turmas=turmas)

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