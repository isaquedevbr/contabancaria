from flask import Flask, render_template, request, redirect, url_for, flash
import random  # Para gerar números de conta simples

app = Flask(__name__)
app.secret_key = 'super_secret_key_para_flash_messages'  # Chave secreta para mensagens flash

# Simula um banco de dados simples em memória
contas = {
    "123456": {"saldo": 1000.00, "nome": "João Silva", "chave_pix": "joao@email.com"},
    "789012": {"saldo": 500.00, "nome": "Maria Souza", "chave_pix": "maria@email.com"}
}


def gerar_numero_conta():
    """Gera um número de conta aleatório de 6 dígitos."""
    while True:
        numero = str(random.randint(100000, 999999))
        if numero not in contas:  # Garante que o número não existe
            return numero


@app.route('/')
def index():
    return render_template('index.html', contas=contas)


@app.route('/criar_conta', methods=['POST'])
def criar_conta():
    nome = request.form['nome_novo_cliente']
    chave_pix = request.form['chave_pix_novo_cliente']

    # Verifica se a chave PIX já existe
    for num_conta, dados in contas.items():
        if dados['chave_pix'] == chave_pix:
            flash('Chave PIX já cadastrada para outra conta. Use uma chave diferente.', 'danger')
            return redirect(url_for('index'))

    novo_numero_conta = gerar_numero_conta()
    contas[novo_numero_conta] = {"saldo": 0.00, "nome": nome, "chave_pix": chave_pix}
    flash(f'Conta para {nome} criada com sucesso! Número da Conta: {novo_numero_conta}.', 'success')
    return redirect(url_for('index'))


@app.route('/depositar', methods=['POST'])
def depositar():
    numero_conta = request.form['numero_conta']
    valor = float(request.form['valor'])

    if numero_conta in contas:
        contas[numero_conta]['saldo'] += valor
        flash(f'Depósito de R$ {valor:.2f} realizado com sucesso na conta {numero_conta}.', 'success')
    else:
        flash('Conta não encontrada.', 'danger')
    return redirect(url_for('index'))


@app.route('/sacar', methods=['POST'])
def sacar():
    numero_conta = request.form['numero_conta']
    valor = float(request.form['valor'])

    if numero_conta in contas:
        if contas[numero_conta]['saldo'] >= valor:
            contas[numero_conta]['saldo'] -= valor
            flash(f'Saque de R$ {valor:.2f} realizado com sucesso da conta {numero_conta}.', 'success')
        else:
            flash('Saldo insuficiente.', 'danger')
    else:
        flash('Conta não encontrada.', 'danger')
    return redirect(url_for('index'))


@app.route('/transferir_pix', methods=['POST'])
def transferir_pix():
    numero_conta_origem = request.form['numero_conta_origem']
    chave_pix_destino = request.form['chave_pix_destino']
    valor = float(request.form['valor'])

    conta_origem = contas.get(numero_conta_origem)

    if not conta_origem:
        flash('Conta de origem não encontrada.', 'danger')
        return redirect(url_for('index'))

    conta_destino = None
    for num_conta, dados in contas.items():
        if dados['chave_pix'] == chave_pix_destino:
            conta_destino = dados
            break

    if not conta_destino:
        flash('Chave PIX de destino não encontrada.', 'danger')
        return redirect(url_for('index'))

    if conta_origem['saldo'] >= valor:
        conta_origem['saldo'] -= valor
        conta_destino['saldo'] += valor
        flash(f'PIX de R$ {valor:.2f} realizado com sucesso de {conta_origem["nome"]} para {conta_destino["nome"]}.',
              'success')
    else:
        flash('Saldo insuficiente na conta de origem.', 'danger')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)