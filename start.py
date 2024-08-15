import subprocess
import os
import time

# Caminho para o arquivo app.py
api_path = os.path.join("api", "app.py")

# Executa o app.py
process = subprocess.Popen(["python", api_path])

# Aguarda um tempo para garantir que o servidor Flask esteja ativo
time.sleep(5)  # Ajuste o tempo conforme necessário

# Executa o main.py
subprocess.run(["python", "main.py"])

# Opcional: esperar o processo app.py terminar (Ctrl+C ou fechamento)
process.wait()