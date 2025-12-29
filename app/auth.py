import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Rota para registrar um novo usuário
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        reg_type = request.form.get('type')
        db = get_db()
        error = None

        if reg_type == 'admin':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif not email:
                error = 'Email is required.'

            if error is None:
                existing = db.execute(
                    'SELECT id FROM Usuarios WHERE username = ? OR email = ?', (username, email)
                ).fetchone()
                if existing is not None:
                    error = 'Username or email already registered.'

            if error is None:
                db.execute(
                    'INSERT INTO Usuarios (username, password, email, papel) VALUES (?, ?, ?, ?)',
                    (username, generate_password_hash(password), email, 'admin')
                )
                db.commit()
                flash('Admin registered successfully.')
                return redirect(url_for('auth.login'))

        elif reg_type == 'professor':
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            departamento = request.form.get('departamento')
            numero_bilhete = request.form.get('numero_bilhete')
            especialidade = request.form.get('especialidade')
            endereco = request.form.get('endereco')
            genero = request.form.get('genero')
            username = request.form.get('username')
            password = request.form.get('password')

            if not nome or not email or not numero_bilhete or not username or not password:
                error = 'Nome, email, número do bilhete, username e password são obrigatórios.'

            if error is None:
                existing_prof = db.execute(
                    'SELECT id FROM Professores WHERE email = ? OR numero_bilhete = ?', (email, numero_bilhete)
                ).fetchone()
                existing_user = db.execute(
                    'SELECT id FROM Usuarios WHERE username = ? OR email = ?', (username, email)
                ).fetchone()
                if existing_prof is not None or existing_user is not None:
                    error = 'Professor ou usuário já registrado com este email ou número do bilhete.'

            if error is None:
                db.execute(
                    'INSERT INTO Professores (nome, email, telefone, departamento, numero_bilhete, especialidade, endereco, genero) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (nome, email, telefone, departamento, numero_bilhete, especialidade, endereco, genero)
                )
                professor_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                db.execute(
                    'INSERT INTO Usuarios (username, password, email, papel, professor_id) VALUES (?, ?, ?, ?, ?)',
                    (username, generate_password_hash(password), email, 'professor', professor_id)
                )
                db.commit()
                flash('Professor registered successfully.')
                return redirect(url_for('auth.login'))

        elif reg_type == 'aluno':
            nome = request.form.get('nome')
            data_nascimento = request.form.get('data_nascimento')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            endereco = request.form.get('endereco')
            numero_bilhete = request.form.get('numero_bilhete')
            genero = request.form.get('genero')
            nome_pai = request.form.get('nome_pai')
            nome_mae = request.form.get('nome_mae')
            telefone_encarregado = request.form.get('telefone_encarregado')
            curso_preferido_id = request.form.get('curso_preferido_id')
            ano_preferido = request.form.get('ano_preferido')
            username = request.form.get('username')
            password = request.form.get('password')

            if not nome or not data_nascimento or not email or not numero_bilhete or not username or not password:
                error = 'Nome, data de nascimento, email, número do bilhete, username e password são obrigatórios.'

            if error is None:
                existing_aluno = db.execute(
                    'SELECT id FROM Alunos WHERE email = ? OR numero_bilhete = ?', (email, numero_bilhete)
                ).fetchone()
                existing_user = db.execute(
                    'SELECT id FROM Usuarios WHERE username = ? OR email = ?', (username, email)
                ).fetchone()
                if existing_aluno is not None or existing_user is not None:
                    error = 'Aluno ou usuário já registrado com este email ou número do bilhete.'

            if error is None:
                db.execute(
                    'INSERT INTO Alunos (nome, data_nascimento, email, telefone, endereco, numero_bilhete, genero, nome_pai, nome_mae, telefone_encarregado, curso_preferido_id, ano_preferido) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (nome, data_nascimento, email, telefone, endereco, numero_bilhete, genero, nome_pai, nome_mae, telefone_encarregado, curso_preferido_id, ano_preferido)
                )
                aluno_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                db.execute(
                    'INSERT INTO Usuarios (username, password, email, papel, aluno_id) VALUES (?, ?, ?, ?, ?)',
                    (username, generate_password_hash(password), email, 'aluno', aluno_id)
                )
                db.commit()
                flash('Aluno registered successfully.')
                return redirect(url_for('auth.login'))

        else:
            error = 'Tipo de registro inválido.'

        flash(error)

    return render_template('auth/register.html')

@bp.route('/pre_register', methods=('GET', 'POST'))
def pre_register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        data_nascimento = request.form.get('data_nascimento')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')
        numero_bilhete = request.form.get('numero_bilhete')
        genero = request.form.get('genero')
        nome_pai = request.form.get('nome_pai')
        nome_mae = request.form.get('nome_mae')
        telefone_encarregado = request.form.get('telefone_encarregado')
        curso_preferido_id = request.form.get('curso_preferido_id')
        ano_preferido = request.form.get('ano_preferido')
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        error = None

        if not nome or not data_nascimento or not email or not numero_bilhete or not username or not password:
            error = 'Nome, data de nascimento, email, número do bilhete, username e password são obrigatórios.'

        if error is None:
            existing_aluno = db.execute(
                'SELECT id FROM Alunos WHERE email = ? OR numero_bilhete = ?', (email, numero_bilhete)
            ).fetchone()
            existing_user = db.execute(
                'SELECT id FROM Usuarios WHERE username = ? OR email = ?', (username, email)
            ).fetchone()
            if existing_aluno is not None or existing_user is not None:
                error = 'Já existe registro com este email ou número do bilhete.'

        if error is None:
            db.execute(
                'INSERT INTO Alunos (nome, data_nascimento, email, telefone, endereco, numero_bilhete, genero, nome_pai, nome_mae, telefone_encarregado, curso_preferido_id, ano_preferido) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (nome, data_nascimento, email, telefone, endereco, numero_bilhete, genero, nome_pai, nome_mae, telefone_encarregado, curso_preferido_id, ano_preferido)
            )
            aluno_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            db.execute(
                'INSERT INTO Usuarios (username, password, email, papel, status, aluno_id) VALUES (?, ?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), email, 'aluno', 'pendente', aluno_id)
            )
            db.commit()
            flash('Pré-inscrição enviada. Aguarde aprovação do administrador.')
            return redirect(url_for('index'))

        flash(error)

    db = get_db()
    cursos = db.execute('SELECT id, nome, descricao FROM Cursos ORDER BY id').fetchall()
    return render_template('auth/pre_register.html', cursos=cursos)


# Rota para fazer login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Usuarios WHERE username = ? or email = ?', (username, username)
        ).fetchone()

        #print("check",[x for x in user])

        if user is None:
            error = 'Usuario não encontrado.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'
        elif user['status'] == 'pendente':
            error = 'Conta pendente de aprovação pelo administrador.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session.modified = True

            return redirect(url_for('index'))

        flash(error)


    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Usuarios WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view