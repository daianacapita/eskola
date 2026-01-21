
from flask import Blueprint, render_template, g, send_file, make_response, request, flash
from app.auth import login_required
import io
import csv
from datetime import datetime

bp = Blueprint('student', __name__, url_prefix='/student')

# Exportar boletim PDF/CSV
@bp.route('/boletim/<int:matricula_id>')
@login_required
def exportar_boletim(matricula_id):
    from flask import g
    from app.db import get_db
    db = get_db()
    if not g.user or g.user['papel'] != 'aluno':
        flash('Acesso restrito a alunos.')
        return redirect(request.referrer or url_for('student.student_area'))
    aluno_id = g.user['aluno_id']
    matricula = db.execute("SELECT * FROM Matriculas WHERE id=? AND aluno_id=? AND status='ativa'", (matricula_id, aluno_id)).fetchone()
    if not matricula:
        flash('Matrícula não encontrada.')
        return redirect(request.referrer or url_for('student.student_area'))
    turma = db.execute(
        '''SELECT t.*, c.nome as curso_nome, c.descricao as curso_desc, a.ano as ano_letivo
           FROM Turmas t
           JOIN Cursos c ON c.id=t.curso_id
           JOIN AnoLectivo a ON a.id=t.ano_lectivo_id
           WHERE t.id=?''',
        (matricula['turma_id'],)
    ).fetchone()
    disciplinas = db.execute(
        '''SELECT d.id, d.nome, d.descricao
           FROM TurmaDisciplinas td
           JOIN Disciplinas d ON d.id=td.disciplina_id
           WHERE td.turma_id=?''',
        (turma['id'],)
    ).fetchall()
    notas = db.execute(
        '''SELECT n.trimestre, d.nome as disciplina_nome, n.nota
           FROM NotasTrimestrais n
           JOIN TurmaDisciplinas td ON td.id=n.turma_disciplina_id
           JOIN Disciplinas d ON d.id=td.disciplina_id
           WHERE n.matricula_id=?
           ORDER BY d.nome, n.trimestre''',
        (matricula_id,)
    ).fetchall()
    # Calcular médias
    medias = {}
    notas_dict = {}
    for n in notas:
        nome = n['disciplina_nome']
        if nome not in notas_dict:
            notas_dict[nome] = {}
        notas_dict[nome][n['trimestre']] = n['nota']
    for d in disciplinas:
        nome = d['nome']
        notas_disc = [notas_dict[nome][tri] for tri in (1,2,3) if nome in notas_dict and tri in notas_dict[nome]]
        if notas_disc:
            medias[nome] = round(sum(notas_disc)/len(notas_disc), 1)
        else:
            medias[nome] = None
    aluno_nome = g.user['username']
    data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M')
    formato = request.args.get('formato', 'pdf')
    if formato == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Disciplina', '1º Tri', '2º Tri', '3º Tri', 'Média'])
        for d in disciplinas:
            nome = d['nome']
            linha = [nome]
            for tri in (1,2,3):
                linha.append(notas_dict[nome][tri] if nome in notas_dict and tri in notas_dict[nome] else '')
            media = medias[nome]
            linha.append(media if media is not None else '')
            writer.writerow(linha)
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=boletim_{aluno_nome}_{turma["designacao"]}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    # PDF via fpdf2
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Boletim Escolar", ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Aluno: {aluno_nome}", ln=True)
    pdf.cell(0, 8, f"Turma: {turma['designacao']} | Ano: {turma['ano']} | Ano Letivo: {turma['ano_letivo']}", ln=True)
    pdf.cell(0, 8, f"Curso: {turma['curso_nome']}", ln=True)
    pdf.cell(0, 8, f"Emitido em: {data_emissao}", ln=True)
    pdf.ln(4)
    # Tabela de notas
    col_widths = [45, 20, 20, 20, 20]
    pdf.set_font("Arial", style="B", size=10)
    headers = ["Disciplina", "1º Tri", "2º Tri", "3º Tri", "Média"]
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for d in disciplinas:
        nome = d['nome']
        pdf.cell(col_widths[0], 8, nome, border=1)
        for tri in (1,2,3):
            nota = str(notas_dict[nome][tri]) if nome in notas_dict and tri in notas_dict[nome] else "—"
            pdf.cell(col_widths[tri], 8, nota, border=1, align="C")
        media = medias[nome]
        media_str = f"{media}" if media is not None else "—"
        if media is not None and media < 10:
            pdf.set_text_color(220, 20, 60)  # vermelho
        else:
            pdf.set_text_color(0, 0, 0)
        pdf.cell(col_widths[4], 8, media_str, border=1, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln()
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 6, "Documento gerado automaticamente pelo sistema eskola.", ln=True, align="C")
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin1')
    pdf_io = io.BytesIO(pdf_bytes)
    return send_file(pdf_io, as_attachment=True, download_name=f'boletim_{aluno_nome}_{turma['designacao']}.pdf', mimetype='application/pdf')


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
        # Calcular médias por disciplina
        medias = {}
        notas_dict = {}
        for n in notas:
            nome = n['disciplina_nome']
            if nome not in notas_dict:
                notas_dict[nome] = {}
            notas_dict[nome][n['trimestre']] = n['nota']
        for d in disciplinas:
            nome = d['nome']
            notas_disc = [notas_dict[nome][tri] for tri in (1,2,3) if nome in notas_dict and tri in notas_dict[nome]]
            if notas_disc:
                medias[nome] = round(sum(notas_disc)/len(notas_disc), 1)
            else:
                medias[nome] = None
        turmas_info.append({
            'turma': turma,
            'disciplinas': disciplinas,
            'tempos': tempos,
            'grade': grade,
            'notas': notas,
            'medias': medias,
        })

    return render_template('student/student_area.html', turmas_info=turmas_info)