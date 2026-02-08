from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from app.db import get_db

bp = Blueprint('perfil', __name__, url_prefix='/perfil')

STATUS_LABELS = {
    'pendente': 'Aguardando aprovacao',
    'aprovado': 'Aprovado',
    'rejeitado': 'Rejeitado',
    'ativo': 'Aprovado'
}

STATUS_STYLES = {
    'pendente': 'status-pendente',
    'aprovado': 'status-aprovado',
    'rejeitado': 'status-rejeitado',
    'ativo': 'status-aprovado'
}


def _get_preinscricao_by_aluno(db, aluno):
    return db.execute(
        '''
        SELECT * FROM PreInscricoes
        WHERE email = ? OR numero_bilhete = ?
        ORDER BY id DESC
        LIMIT 1
        ''',
        (aluno['email'], aluno['numero_bilhete'])
    ).fetchone()


@bp.route('/', defaults={'aluno_id': None})
@bp.route('/<int:aluno_id>')
@login_required
def perfil(aluno_id):
    db = get_db()
    is_admin = g.user['papel'] == 'admin'
    
    # Controle de acesso
    if not is_admin:
        if g.user['papel'] != 'aluno':
            flash('Acesso negado.')
            return redirect(url_for('index'))
        # Aluno: acesso apenas ao próprio perfil
        if aluno_id is None:
            aluno_id = g.user['aluno_id']
        elif aluno_id != g.user['aluno_id']:
            flash('Acesso negado: você só pode ver seu próprio perfil.')
            return redirect(url_for('index'))
    else:
        # Admin: precisa especificar um ID
        if aluno_id is None:
            flash('Informe o ID do aluno.')
            return redirect(url_for('index'))

    aluno = None
    preinscricao = None

    # Buscar dados em Alunos (aluno aprovado/matriculado)
    if aluno_id is not None:
        aluno = db.execute('SELECT * FROM Alunos WHERE id = ?', (aluno_id,)).fetchone()

    # Se encontrou aluno aprovado, buscar também a pré-inscrição (para histórico de docs)
    if aluno:
        preinscricao = _get_preinscricao_by_aluno(db, aluno)
    # Se não encontrou aluno aprovado, procurar em PreInscricoes (pendente/rejeitado)
    elif is_admin:
        preinscricao = db.execute(
            'SELECT * FROM PreInscricoes WHERE id = ?', (aluno_id,)
        ).fetchone()

    if not aluno and not preinscricao:
        flash('Perfil não encontrado.')
        return redirect(url_for('index'))

    perfil_data = aluno if aluno else preinscricao

    curso = None
    if perfil_data and perfil_data['curso_preferido_id']:
        curso = db.execute(
            'SELECT nome FROM Cursos WHERE id = ?', (perfil_data['curso_preferido_id'],)
        ).fetchone()

    # Determinar status baseado na origem dos dados
    status_value = None
    data_source = None  # 'aluno' ou 'preinscricao'
    if aluno:
        # Aluno aprovado/matriculado: status vem do usuário
        data_source = 'aluno'
        if is_admin:
            status_value = 'ativo'
        else:
            status_value = g.user['status'] if g.user['papel'] == 'aluno' else 'ativo'
    elif preinscricao:
        # Pré-inscrição pendente/rejeitada
        data_source = 'preinscricao'
        status_value = preinscricao['status']

    status_label = STATUS_LABELS.get(status_value, 'Sem status')
    status_style = STATUS_STYLES.get(status_value, 'status-pendente')

    turmas = []
    if preinscricao and preinscricao['curso_preferido_id'] and preinscricao['ano_preferido']:
        turmas = db.execute(
            '''
            SELECT t.id, t.designacao, c.nome as curso_nome
            FROM Turmas t
            JOIN Cursos c ON t.curso_id = c.id
            WHERE t.curso_id = ? AND t.ano = ?
            ''',
            (preinscricao['curso_preferido_id'], preinscricao['ano_preferido'])
        ).fetchall()

    return render_template(
        'perfil.html',
        perfil=perfil_data,
        aluno=aluno,
        curso=curso,
        preinscricao=preinscricao,
        status_label=status_label,
        status_style=status_style,
        data_source=data_source,
        turmas=turmas,
        is_admin=is_admin
    )
