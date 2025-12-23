import uvicorn
import os
import sys

# Corrección de ruta
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir) 

if __name__ == "__main__":
    print("🚀 Iniciando servidor: src.main:app")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)