#!/usr/bin/env python3
"""
Script de inicio para la aplicación FastAPI
"""

import os
import sys
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Función principal para iniciar la aplicación"""
    try:
        # Obtener el puerto desde las variables de entorno
        port = int(os.getenv("PORT", 8080))
        
        logger.info(f"🚀 Starting server from start.py...")
        logger.info(f"📁 Current directory: {os.getcwd()}")
        logger.info(f"🔧 PORT environment variable: {port}")
        logger.info(f"🐍 Python version: {sys.version}")
        
        # Importar la aplicación desde main_simple.py
        from main_simple import app
        
        logger.info(f"🌐 Starting uvicorn server on port {port}")
        
        # Iniciar el servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 