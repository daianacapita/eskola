import functools
import os
import uuid
from pathlib import Path

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, send_file)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configurações de upload
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_obj, max_size=MAX_FILE_SIZE):
    """Verifica o tamanho do arquivo."""
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    return size <= max_size

def save_uploaded_file(file_obj, preinscricao_id, file_type):
    """
    Salva o arquivo de forma segura.
    file_type: 'documento_anterior' ou 'bilhete'
    Retorna o caminho relativo do arquivo ou None se houver erro.
    """
    if not file_obj or file_obj.filename == '':
        return None
    
    if not allowed_file(file_obj.filename):
        return None
    
    if not validate_file_size(file_obj):
        return None
    
    # Criar diretório para a pré-inscrição se não existir
    base_upload_dir = os.path.join(
        current_app.root_path, '..', 'uploads', 'preinscricao', str(preinscricao_id)
    )
    base_upload_dir = os.path.normpath(base_upload_dir)
    os.makedirs(base_upload_dir, exist_ok=True)
    
    # Obter extensão do arquivo
    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    
    # Gerar nome único para o arquivo
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Caminho completo para salvar
    file_path = os.path.join(base_upload_dir, file_type, unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        # Salvar arquivo
        file_obj.save(file_path)
        # Retornar caminho relativo para armazenar no BD
        return os.path.join('uploads', 'preinscricao', str(preinscricao_id), file_type, unique_filename)
    except Exception:
        return None

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
        
        # Obter arquivos
        documento_anterior = request.files.get('documento_anterior')
        bilhete = request.files.get('bilhete')
        
        db = get_db()
        error = None

        # Validações básicas
        if not nome or not data_nascimento or not email or not numero_bilhete or not username or not password:
            error = 'Nome, data de nascimento, email, número do bilhete, username e password são obrigatórios.'
        
        # Validar documentos obrigatórios
        if error is None:
            if not documento_anterior or documento_anterior.filename == '':
                error = 'Certificado/declaração da classe anterior é obrigatório.'
            elif not bilhete or bilhete.filename == '':
                error = 'Bilhete de Identidade é obrigatório.'

        # Verificar se email ou bilhete já existem
        if error is None:
            existing_preinscricao = db.execute(
                'SELECT id FROM PreInscricoes WHERE email = ? OR numero_bilhete = ?',
                (email, numero_bilhete)
            ).fetchone()
            existing_aluno = db.execute(
                'SELECT id FROM Alunos WHERE email = ? OR numero_bilhete = ?',
                (email, numero_bilhete)
            ).fetchone()
            existing_user = db.execute(
                'SELECT id FROM Usuarios WHERE username = ? OR email = ?',
                (username, email)
            ).fetchone()
            if existing_preinscricao is not None or existing_aluno is not None or existing_user is not None:
                error = 'Já existe um registro com este email ou número do bilhete.'

        # Salvar pré-inscrição primeiro para obter ID
        if error is None:
            try:
                db.execute(
                    '''INSERT INTO PreInscricoes 
                    (nome, data_nascimento, email, telefone, endereco, numero_bilhete, 
                     genero, nome_pai, nome_mae, telefone_encarregado, curso_preferido_id, 
                     ano_preferido, username, password) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nome, data_nascimento, email, telefone, endereco, numero_bilhete,
                     genero, nome_pai, nome_mae, telefone_encarregado, curso_preferido_id,
                     ano_preferido, username, generate_password_hash(password))
                )
                db.commit()
                preinscricao_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            except Exception as e:
                error = 'Erro ao salvar pré-inscrição. Tente novamente.'

        # Salvar documentos
        if error is None:
            doc_anterior_path = save_uploaded_file(documento_anterior, preinscricao_id, 'documento_anterior')
            bilhete_path = save_uploaded_file(bilhete, preinscricao_id, 'bilhete')
            
            if not doc_anterior_path:
                error = 'Erro ao salvar certificado/declaração. Certifique-se de que é PDF ou imagem (JPG/PNG) e não excede 4MB.'
            elif not bilhete_path:
                error = 'Erro ao salvar Bilhete de Identidade. Certifique-se de que é PDF ou imagem (JPG/PNG) e não excede 4MB.'

        # Atualizar paths dos documentos no banco de dados
        if error is None:
            try:
                db.execute(
                    'UPDATE PreInscricoes SET documento_anterior_path = ?, bilhete_path = ? WHERE id = ?',
                    (doc_anterior_path, bilhete_path, preinscricao_id)
                )
                db.commit()
                flash('Pré-inscrição enviada com sucesso. Aguarde aprovação do administrador.')
                return redirect(url_for('index'))
            except Exception as e:
                error = 'Erro ao registrar documentos. Tente novamente.'

        # Se houver erro, limpar a pré-inscrição criada
        if error is not None and 'preinscricao_id' in locals():
            try:
                db.execute('DELETE FROM PreInscricoes WHERE id = ?', (preinscricao_id,))
                db.commit()
            except:
                pass
        
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

@bp.route('/download_documento/<int:preinscricao_id>/<doc_type>')
@login_required
def download_documento(preinscricao_id, doc_type):
    """
    Download seguro de documento. Admin ou aluno dono do documento pode acessar.
    """
    # Validar doc_type
    if doc_type not in ['documento_anterior', 'bilhete']:
        flash('Tipo de documento inválido.')
        return redirect(url_for('index'))
    
    db = get_db()
    preinscricao = db.execute(
        'SELECT * FROM PreInscricoes WHERE id = ?', (preinscricao_id,)
    ).fetchone()
    
    if not preinscricao:
        flash('Pré-inscrição não encontrada.')
        return redirect(url_for('index'))
    
    # Permissão: admin ou aluno dono
    if g.user['papel'] == 'admin':
        pass
    elif g.user['papel'] == 'aluno':
        aluno = db.execute(
            'SELECT * FROM Alunos WHERE id = ?', (g.user['aluno_id'],)
        ).fetchone()
        if not aluno:
            flash('Acesso negado.')
            return redirect(url_for('index'))
        if preinscricao['email'] != aluno['email'] and preinscricao['numero_bilhete'] != aluno['numero_bilhete']:
            flash('Acesso negado.')
            return redirect(url_for('index'))
    else:
        flash('Acesso negado.')
        return redirect(url_for('index'))
    
    # Obter o caminho do documento
    if doc_type == 'documento_anterior':
        file_path = preinscricao['documento_anterior_path']
    else:
        file_path = preinscricao['bilhete_path']
    
    if not file_path:
        flash('Documento não encontrado.')
        return redirect(url_for('index'))
    
    # Converter arquivo relativo para caminho absoluto de forma segura
    # Prevenir path traversal attacks
    full_path = os.path.normpath(os.path.join(current_app.root_path, '..', file_path))
    base_dir = os.path.normpath(os.path.join(current_app.root_path, '..', 'uploads', 'preinscricao'))
    
    # Garantir que o arquivo está dentro do diretório permitido
    if not full_path.startswith(base_dir) or not os.path.exists(full_path):
        flash('Acesso negado ao documento.')
        return redirect(url_for('index'))
    
    try:
        return send_file(full_path, as_attachment=True, download_name=os.path.basename(full_path))
    except Exception:
        flash('Erro ao baixar documento.')
        return redirect(url_for('index'))