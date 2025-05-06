import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from iqoptionapi.stable_api import IQ_Option
import time
import csv
from datetime import datetime
import os

# Variáveis globais
executando = False
api = None
ativo = ""
valor_operacao = 2
tempo_expiracao = 1

# Ativos disponíveis
ativos_disponiveis = ["EURUSD", "EURUSD-OTC"]


# Funções auxiliares
def log(msg):
    log_box.insert(tk.END, msg + '\n')
    log_box.see(tk.END)

def registrar_resultado(data_hora, ativo, tipo, valor, preco, resultado, lucro):
    arquivo = 'historico_operacoes.csv'
    existe = os.path.isfile(arquivo)
    with open(arquivo, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        if not existe:
            writer.writerow(["Data e Hora", "Ativo", "Tipo", "Valor", "Preço Entrada", "Resultado", "Lucro/Prejuízo"])
        writer.writerow([data_hora, ativo, tipo.upper(), valor, preco, resultado, lucro])

def pontos(p1, p2):
    return abs(int(round((p2 - p1) * 100000)))

def esperar_hora_cheia():
    agora = datetime.now()
    segundos_restantes = 60 - agora.second - agora.microsecond / 1_000_000
    time.sleep(segundos_restantes)

def validar_ativo_binario(ativo):
    try:
        candles = api.get_candles(ativo, 60, 1, time.time())
        if candles:
            log(f"✅ Ativo {ativo} está operável com candles disponíveis.")
            return True
        else:
            log(f"⚠️ Ativo {ativo} não está retornando candles. Provavelmente fechado.")
            return False
    except Exception as e:
        log(f"❌ Erro ao validar ativo {ativo}: {e}")
        return False


def conectar():
    global api
    email = "seu email"
    senha = "sua senha"
    conta = "demo / real"

    api = IQ_Option(email, senha)
    api.connect()

    if api.check_connect():
        log("✅ Conectado com sucesso!")
        api.change_balance("REAL" if conta == "real" else "PRACTICE")
        log(f"💰 Saldo atual: ${api.get_balance():.2f}")
    else:
        log("❌ Falha na conexão.")

def tendencia_alta(api, ativo):
    candles = api.get_candles(ativo, 60, 2, time.time())
    precos = [candle['close'] for candle in candles]
    return precos[-1] > precos[0]

def executar_put():
    preco_inicial = api.get_candles(ativo, 1, 1, time.time())[0]['close']
    preco_topo = preco_inicial
    subiu, caiu = False, False
    tempo_inicio = datetime.now()

    while (datetime.now() - tempo_inicio).seconds < 30:
        preco_atual = api.get_candles(ativo, 1, 1, time.time())[0]['close']

        if not subiu and pontos(preco_inicial, preco_atual) >= 5 and preco_atual > preco_inicial:
            subiu = True
            preco_topo = preco_atual
            log(f"📈 Subida: {preco_inicial} → {preco_topo}")

        if subiu and not caiu and pontos(preco_topo, preco_atual) >= 3 and preco_atual < preco_topo:
            preco_recuo = preco_atual
            caiu = True
            log(f"📉 Recuo: {preco_topo} → {preco_recuo}")

            tempo_estavel = time.time()
            preco_base = preco_recuo
            estabilidade_confirmada = True

            while time.time() - tempo_estavel < 1:
                preco_verificacao = api.get_candles(ativo, 1, 1, time.time())[0]['close']
                if preco_verificacao != preco_base:
                    log("↪️ Preço se mexeu! Cancelando sinal de estabilidade.")
                    estabilidade_confirmada = False
                    break

            if estabilidade_confirmada:
                preco_final = api.get_candles(ativo, 1, 1, time.time())[0]['close']
                if pontos(preco_recuo, preco_final) >= 1 and preco_final < preco_recuo:
                    hora_entrada = datetime.now().strftime('%H:%M:%S')
                    log(f"🎯 Abrindo PUT às {hora_entrada}")
                    status, id_op = api.buy(valor_operacao, ativo, 'put', tempo_expiracao)

                    if status:
                        log(f"✅ Operação aberta! (ID: {id_op})")
                        time.sleep((tempo_expiracao * 60) + 2)
                        resultado, lucro = api.check_win_v4(id_op)
                        data_hora = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

                        if resultado == 'win':
                            log(f"🏆 WIN! Lucro: {lucro:.2f}")
                            registrar_resultado(data_hora, ativo, 'PUT', valor_operacao, preco_final, 'WIN', round(lucro, 2))
                        elif resultado == 'loose':
                            log(f"🚫 LOSS! Prejuízo: {lucro:.2f}")
                            registrar_resultado(data_hora, ativo, 'PUT', valor_operacao, preco_final, 'LOSS', round(lucro, 2))
                        else:
                            log("⚠️ EMPATE.")
                            registrar_resultado(data_hora, ativo, 'PUT', valor_operacao, preco_final, 'EMPATE', 0.00)
                    else:
                        log("❌ Erro ao abrir operação.")
                    return
    if not subiu or not caiu:
        log("🚫 Nenhum sinal PUT detectado.")

def executar_call():
    preco_inicial = api.get_candles(ativo, 1, 1, time.time())[0]['close']
    preco_fundo = preco_inicial
    caiu, subiu = False, False
    tempo_inicio = datetime.now()

    while (datetime.now() - tempo_inicio).seconds < 30:
        preco_atual = api.get_candles(ativo, 1, 1, time.time())[0]['close']

        if not caiu and pontos(preco_inicial, preco_atual) >= 5 and preco_atual < preco_inicial:
            caiu = True
            preco_fundo = preco_atual
            log(f"📉 Queda: {preco_inicial} → {preco_fundo}")

        if caiu and not subiu and pontos(preco_fundo, preco_atual) >= 3 and preco_atual > preco_fundo:
            preco_reacao = preco_atual
            subiu = True
            log(f"📈 Reação: {preco_fundo} → {preco_reacao}")

            tempo_estavel = time.time()
            preco_base = preco_reacao
            estabilidade_confirmada = True

            while time.time() - tempo_estavel < 1:
                preco_verificacao = api.get_candles(ativo, 1, 1, time.time())[0]['close']
                if preco_verificacao != preco_base:
                    log("↪️ Preço se mexeu! Cancelando sinal de estabilidade.")
                    estabilidade_confirmada = False
                    break

            if estabilidade_confirmada:
                while (datetime.now() - tempo_inicio).seconds < 30:
                    preco_final = api.get_candles(ativo, 1, 1, time.time())[0]['close']
                    if pontos(preco_reacao, preco_final) >= 2 and preco_final > preco_reacao:
                        hora_entrada = datetime.now().strftime('%H:%M:%S')
                        log(f"🎯 Abrindo CALL às {hora_entrada}")
                        status, id_op = api.buy(valor_operacao, ativo, 'call', tempo_expiracao)

                        if status:
                            log(f"✅ Operação aberta! (ID: {id_op})")
                            time.sleep((tempo_expiracao * 60) + 2)
                            resultado, lucro = api.check_win_v4(id_op)
                            data_hora = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

                            if resultado == 'win':
                                log(f"🏆 WIN! Lucro: {lucro:.2f}")
                                registrar_resultado(data_hora, ativo, 'CALL', valor_operacao, preco_final, 'WIN', round(lucro, 2))
                            elif resultado == 'loose':
                                log(f"🚫 LOSS! Prejuízo: {lucro:.2f}")
                                registrar_resultado(data_hora, ativo, 'CALL', valor_operacao, preco_final, 'LOSS', round(lucro, 2))
                            else:
                                log("⚠️ EMPATE.")
                                registrar_resultado(data_hora, ativo, 'CALL', valor_operacao, preco_final, 'EMPATE', 0.00)
                        else:
                            log("❌ Erro ao abrir operação CALL.")
                        return
    if not caiu or not subiu:
        log("🚫 Nenhum sinal CALL detectado.")

def iniciar_analise():
    log("🟢 Iniciando análise...")
    global executando, ativo, valor_operacao
    executando = True
    ativo = ativo_var.get()

    if not validar_ativo_binario(ativo):
        messagebox.showerror("Ativo inválido", f"O ativo '{ativo}' não está disponível.")
        return

    try:
        valor_operacao = float(valor_entry.get())
    except:
        messagebox.showerror("Erro", "Digite um valor válido.")
        return

    def run():
        while executando:
            esperar_hora_cheia()
            agora = datetime.now().strftime('%H:%M:%S')
            log(f"\n🔍 [{ativo}] Análise às {agora}")

            if not tendencia_alta(api, ativo):
                log(f"⚠️ [{ativo}] Tendência não favorável.")
                continue

            if operar_put_var.get():
                executar_put()
            if operar_call_var.get():
                executar_call()

    threading.Thread(target=run, daemon=True).start()

def parar_analise():
    global executando
    executando = False
    log("🛑 Análise finalizada.")
    janela.quit()

# Interface gráfica
janela = tk.Tk()
janela.title("Robô de Análise - IQ Option")
janela.geometry("700x620")
janela.configure(bg="#f7f7f7")
ativo_var = tk.StringVar(value=ativos_disponiveis[0])


frame_login = tk.LabelFrame(janela, text="Login", padx=10, pady=10)
frame_login.pack(pady=10, fill="x", padx=10)

tk.Label(frame_login, text="Email:").grid(row=0, column=0, sticky='w')
email_entry = tk.Entry(frame_login, width=30)
email_entry.insert(0, 'felipecdm04@gmail.com')
email_entry.grid(row=0, column=1)

tk.Label(frame_login, text="Senha:").grid(row=1, column=0, sticky='w')
senha_entry = tk.Entry(frame_login, show="*", width=30)
senha_entry.insert(0, '08fortoday123')
senha_entry.grid(row=1, column=1)

conta_var = tk.StringVar(value="demo")
tk.Radiobutton(frame_login, text="Demo", variable=conta_var, value="demo").grid(row=2, column=0, sticky='w')
tk.Radiobutton(frame_login, text="Real", variable=conta_var, value="real").grid(row=2, column=1, sticky='w')

tk.Button(frame_login, text="Conectar", command=conectar).grid(row=3, column=0, columnspan=2, pady=5)

frame_config = tk.LabelFrame(janela, text="Configurações", padx=10, pady=10)
frame_config.pack(pady=10, fill="x", padx=10)

tk.Label(frame_config, text="Ativo:").grid(row=0, column=0, sticky='w')
tk.OptionMenu(frame_config, ativo_var, *ativos_disponiveis).grid(row=0, column=1, sticky='w')

tk.Label(frame_config, text="Valor da Operação:").grid(row=1, column=0, sticky='w')
valor_entry = tk.Entry(frame_config, width=10)
valor_entry.insert(0, "2")
valor_entry.grid(row=1, column=1, sticky='w')

tk.Label(frame_config, text="Estratégias:").grid(row=2, column=0, sticky='w')
operar_put_var = tk.BooleanVar(value=True)
operar_call_var = tk.BooleanVar(value=False)
tk.Checkbutton(frame_config, text="PUT", variable=operar_put_var).grid(row=2, column=1, sticky='w')
tk.Checkbutton(frame_config, text="CALL", variable=operar_call_var).grid(row=2, column=2, sticky='w')

frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="▶ Iniciar Análise", command=iniciar_analise, width=20, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
tk.Button(frame_botoes, text="⛔ Parar e Fechar", command=parar_analise, width=20, bg="#f44336", fg="white").grid(row=0, column=1, padx=10)

log_box = scrolledtext.ScrolledText(janela, width=90, height=20, bg="#000000", fg="#00FF00", font=('Consolas', 10))
log_box.pack(pady=10, padx=10)

janela.mainloop()
