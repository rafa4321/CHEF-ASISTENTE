import uvicorn
import os

if __name__ == "__main__":
    # OBTENER PUERTO DE RENDER O USAR 8000 POR DEFECTO
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Iniciando servidor en el puerto: {port}")
    # Importamos 'main' (el archivo) y 'app' (la instancia de FastAPI)
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)