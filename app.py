from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import pandas as pd
import pdfkit
import re
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Troque por algo seguro em produção!

# Configuração do banco SQLite com SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos do banco
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # user ou admin

class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    livro = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    devolvido = db.Column(db.Boolean, default=False)

    usuario = db.relationship('User', backref=db.backref('historicos', lazy=True))

# Dados dos livros em memória
LIVROS = {
    'Clean Code': {'quantidade': 5, 'reservas': []},
    'Python Fluente': {'quantidade': 3, 'reservas': []},
    'Flask Web': {'quantidade': 4, 'reservas': []},
}

# Email mock (só printa)
def enviar_email(destino, assunto, corpo):
    print(f"Enviando email para {destino}\nAssunto: {assunto}\nCorpo:\n{corpo}")

# Validação CPF simples (só formato)
def validar_cpf(cpf):
    return bool(re.fullmatch(r'\d{11}', cpf))

# Decoradores para login e admin
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor faça login primeiro.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor faça login primeiro.", "error")
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            flash("Acesso negado. Apenas admins.", "error")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrapped

@app.route('/')
@login_required
def home():
    user = User.query.get(session['user_id'])

    # Pegando os filtros de busca da query string
    titulo_filtro = request.args.get('titulo', '').strip().lower()
    autor_filtro = request.args.get('autor', '').strip().lower()
    ano_filtro = request.args.get('ano', '').strip()

    # Paginação
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 5  # livros por página

    # Simulando os dados dos livros com autor e ano (você pode expandir isso no futuro)
    livros_completos = [
        {'titulo': 'Clean Code', 'autor': 'Robert C. Martin', 'ano': '2008', 'quantidade_disponivel': LIVROS['Clean Code']['quantidade']},
        {'titulo': 'Python Fluente', 'autor': 'Luciano Ramalho', 'ano': '2015', 'quantidade_disponivel': LIVROS['Python Fluente']['quantidade']},
        {'titulo': 'Flask Web', 'autor': 'Miguel Grinberg', 'ano': '2018', 'quantidade_disponivel': LIVROS['Flask Web']['quantidade']},
        # Adicione mais livros se quiser
    ]

    # Filtrando
    livros_filtrados = []
    for livro in livros_completos:
        if titulo_filtro and titulo_filtro not in livro['titulo'].lower():
            continue
        if autor_filtro and autor_filtro not in livro['autor'].lower():
            continue
        if ano_filtro and ano_filtro != livro['ano']:
            continue
        livros_filtrados.append(livro)

    # Paginação real
    total_paginas = max((len(livros_filtrados) - 1) // por_pagina + 1, 1)
    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    livros_pagina = livros_filtrados[inicio:fim]

    return render_template('home.html',
                           user=user,
                           livros=livros_pagina,
                           busca={'titulo': titulo_filtro, 'autor': autor_filtro, 'ano': ano_filtro},
                           pagina=pagina,
                           total_paginas=total_paginas)

# <<< ROTA LOGIN ÚNICA E CORRETA >>> 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, senha):
            session['user_id'] = user.id
            flash(f"Bem-vindo, {user.username}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuário ou senha inválidos.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da sessão.", "success")
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['password']
        senha_confirm = request.form['password_confirm']
        if senha != senha_confirm:
            flash("As senhas não conferem.", "error")
            return redirect(url_for('cadastro'))
        if User.query.filter_by(username=username).first():
            flash("Usuário já existe.", "error")
            return redirect(url_for('cadastro'))
        novo_usuario = User(
            username=username,
            password_hash=generate_password_hash(senha),
            role='user'  # padrão é user
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/emprestar', methods=['GET', 'POST'])
@login_required
def emprestar():
    if request.method == 'POST':
        cpf = request.form.get('cpf', '').strip()
        livro = request.form.get('titulo', '').strip()

        if not validar_cpf(cpf):
            flash("CPF inválido. Use somente números (11 dígitos).", "error")
            return redirect(url_for('emprestar'))

        if livro not in LIVROS:
            flash("Livro inválido.", "error")
            return redirect(url_for('emprestar'))

        if LIVROS[livro]['quantidade'] <= 0:
            flash("Livro indisponível. Você pode reservar.", "error")
            return redirect(url_for('emprestar'))

        LIVROS[livro]['quantidade'] -= 1
        user = User.query.get(session['user_id'])
        historico = Historico(
            usuario_id=user.id,
            cpf=cpf,
            livro=livro,
            data=datetime.datetime.now(),
            devolvido=False
        )
        db.session.add(historico)
        db.session.commit()

        flash(f"Empréstimo do livro '{livro}' realizado com sucesso!", "success")

        enviar_email(
            destino=f"{cpf}@exemplo.com",
            assunto="Confirmação de empréstimo",
            corpo=f"Você emprestou o livro '{livro}'. Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        return redirect(url_for('emprestar'))  # Ou para 'home' se preferir

    # Se GET, renderiza o formulário, passando a lista de livros
    return render_template('emprestar.html', livros=LIVROS.keys())

@app.route('/devolver', methods=['GET', 'POST'])
@login_required
def devolver():
    if request.method == 'POST':
        cpf = request.form.get('cpf', '').strip()
        livro = request.form.get('titulo', '').strip()

        if not validar_cpf(cpf):
            flash("CPF inválido para devolução.", "error")
            return redirect(url_for('devolver'))

        historico = Historico.query.filter_by(cpf=cpf, livro=livro, devolvido=False).first()
        if not historico:
            flash("Empréstimo não encontrado ou já devolvido.", "error")
            return redirect(url_for('devolver'))

        historico.devolvido = True
        LIVROS[livro]['quantidade'] += 1
        db.session.commit()

        flash(f"Livro '{livro}' devolvido com sucesso!", "success")
        return redirect(url_for('home'))

    return render_template('devolver.html')

@app.route('/reservar', methods=['POST'])
@login_required
def reservar():
    cpf = request.form.get('cpf', '').strip()
    livro = request.form.get('titulo', '').strip()
    user = User.query.get(session['user_id'])

    if not validar_cpf(cpf):
        flash("CPF inválido para reserva.", "error")
        return redirect(url_for('home'))
    if livro not in LIVROS:
        flash("Livro inválido para reserva.", "error")
        return redirect(url_for('home'))
    if user.username in LIVROS[livro]['reservas']:
        flash("Você já reservou esse livro.", "error")
        return redirect(url_for('home'))

    LIVROS[livro]['reservas'].append(user.username)
    flash(f"Reserva para '{livro}' realizada!", "success")
    return redirect(url_for('home'))

@app.route('/historico')
@login_required
def historico():
    user = User.query.get(session['user_id'])
    if user.role == 'admin':
        registros = Historico.query.all()
    else:
        registros = Historico.query.filter_by(usuario_id=user.id).all()

    return render_template('historico.html', registros=registros)

@app.route('/exportar_excel')
@admin_required
def exportar_excel():
    registros = Historico.query.all()
    data = []
    for r in registros:
        data.append({
            'Usuário': r.usuario.username,
            'CPF': r.cpf,
            'Livro': r.livro,
            'Data': r.data.strftime('%d/%m/%Y %H:%M'),
            'Devolvido': 'Sim' if r.devolvido else 'Não'
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Historico')
    output.seek(0)
    return send_file(output,
                     attachment_filename="historico.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/exportar_pdf')
@admin_required
def exportar_pdf():
    registros = Historico.query.all()
    # Gerar HTML para PDF
    html = render_template('historico_pdf.html', registros=registros)
    pdf = pdfkit.from_string(html, False)
    return send_file(BytesIO(pdf),
                     attachment_filename="historico.pdf",
                     as_attachment=True,
                     mimetype='application/pdf')

@app.route('/relatorios')
@admin_required
def relatorios():
    total_livros = len(LIVROS)
    total_usuarios = User.query.count()
    total_emprestimos = Historico.query.count()

    # Contagem de livros emprestados
    contagem_livros = {}
    for h in Historico.query.all():
        contagem_livros[h.livro] = contagem_livros.get(h.livro, 0) + 1
    livros_mais_emprestados = sorted(contagem_livros.items(), key=lambda x: x[1], reverse=True)

    # Usuários com empréstimos ativos
    usuarios = User.query.all()
    usuarios_ativos = []
    for u in usuarios:
        qtd_ativos = Historico.query.filter_by(usuario_id=u.id, devolvido=False).count()
        if qtd_ativos > 0:
            usuarios_ativos.append({
                'nome': u.username,
                'cpf': Historico.query.filter_by(usuario_id=u.id).first().cpf,
                'qtd_emprestimos_ativos': qtd_ativos
            })

    # Dados para o gráfico
    livros_labels = [item[0] for item in livros_mais_emprestados]
    livros_data = [item[1] for item in livros_mais_emprestados]

    return render_template('relatorios.html',
                           total_livros=total_livros,
                           total_usuarios=total_usuarios,
                           total_emprestimos=total_emprestimos,
                           livros_mais_emprestados=livros_mais_emprestados,
                           usuarios_ativos=usuarios_ativos,
                           livros_labels=livros_labels,
                           livros_data=livros_data)

@app.route('/criar_admin', methods=['GET', 'POST'])
def criar_admin():
    # Para segurança, só disponível em debug (modo dev)
    if not app.debug:
        return "Acesso negado.", 403

    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['password']
        senha_confirm = request.form['password_confirm']
        if senha != senha_confirm:
            flash("As senhas não conferem.", "error")
            return redirect(url_for('criar_admin'))
        if User.query.filter_by(username=username).first():
            flash("Usuário já existe.", "error")
            return redirect(url_for('criar_admin'))

        novo_admin = User(
            username=username,
            password_hash=generate_password_hash(senha),
            role='admin'
        )
        db.session.add(novo_admin)
        db.session.commit()
        flash("Admin criado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('criar_admin.html')

@app.route('/dashboard_usuario')
@login_required
def usuario_dashboard():
    usuario = User.query.get(session['user_id'])
    return render_template('usuario_dashboard.html', usuario=usuario)
# Rota nova para "Biblioteca" chamar os relatórios
@app.route('/biblioteca')
@admin_required
def biblioteca():
    return relatorios()

# <<< ROTA CRIAR ADMIN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco
    print(app.url_map)
    app.run(debug=True)

