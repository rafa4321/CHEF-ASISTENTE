import uvicorn
import os

if __name__ == "__main__":
    # Render asigna un puerto automáticamente
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Servidor arrancando en puerto: {port}")
    
    # IMPORTANTE: "src.main:app" le dice que entre a la carpeta 'src' 
    # y busque el archivo 'main.py' donde definiste 'app = FastAPI()'
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)