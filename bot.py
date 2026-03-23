import requests
import time
import threading

TOKEN = "8662346513:AAECbjkiaVALvXJFJra9Bv8jMPUlTVn2YaU"

url_base = f"https://api.telegram.org/bot{TOKEN}"

ultimo_update = None

arquivo = "tarefas.txt"

# carregar tarefas salvas
try:
    with open(arquivo, "r") as f:
        tarefas = f.read().splitlines()
except:
    tarefas = []

print("Bot iniciado...")

while True:
    resposta = requests.get(url_base + "/getUpdates").json()

    if resposta["result"]:
        for update in resposta["result"]:
            update_id = update["update_id"]

            if ultimo_update is None or update_id > ultimo_update:
                ultimo_update = update_id

                if "message" not in update:
                    continue

                mensagem = update["message"]["text"]
                chat_id = update["message"]["chat"]["id"]

                # COMANDOS
                if mensagem == "/start":
                    resposta_texto = "Olá! Eu sou seu bot de tarefas."

                elif mensagem == "/help":
                    resposta_texto = "Comandos:\n/add tarefa\n/list\n/remove número\n/remind minutos mensagem"

                elif mensagem.startswith("/add"):
                    tarefa = mensagem.replace("/add ", "")
                    tarefas.append(tarefa)

                    with open(arquivo, "w") as f:
                        for t in tarefas:
                            f.write(t + "\n")

                    resposta_texto = "Tarefa adicionada!"

                elif mensagem == "/list":
                    if not tarefas:
                        resposta_texto = "Nenhuma tarefa ainda."
                    else:
                        resposta_texto = "Suas tarefas:\n"
                        for i, t in enumerate(tarefas, 1):
                            resposta_texto += f"{i}. {t}\n"

                elif mensagem.startswith("/remove"):
                    try:
                        numero = int(mensagem.split(" ")[1]) - 1
                        tarefa_removida = tarefas.pop(numero)

                        with open(arquivo, "w") as f:
                            for t in tarefas:
                                f.write(t + "\n")

                        resposta_texto = f"Tarefa removida: {tarefa_removida}"

                    except:
                        resposta_texto = "Número inválido."

                elif mensagem.startswith("/remind"):
                    try:
                        partes = mensagem.split(" ")
                        minutos = int(partes[1])
                        texto = " ".join(partes[2:])

                        resposta_texto = f"Ok! Vou te lembrar em {minutos} minuto(s)."

                        requests.post(
                            url_base + "/sendMessage",
                            data={
                                "chat_id": chat_id,
                                "text": resposta_texto
                            }
                        )

                        def enviar_lembrete():
                            time.sleep(minutos * 60)
                            requests.post(
                                url_base + "/sendMessage",
                                data={
                                    "chat_id": chat_id,
                                    "text": f"⏰ Lembrete: {texto}"
                                }
                            )

                        threading.Thread(target=enviar_lembrete).start()
                        continue

                    except:
                        resposta_texto = "Uso correto: /remind 10 mensagem"

                else:
                    resposta_texto = "Comando não reconhecido."

                requests.post(
                    url_base + "/sendMessage",
                    data={
                        "chat_id": chat_id,
                        "text": resposta_texto
                    }
                )

    time.sleep(2)
