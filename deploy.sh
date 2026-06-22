#!/bin/bash
# SaludApp Peru — Deploy script para VPS Ubuntu 22.04
# Ejecutar: chmod +x deploy.sh && ./deploy.sh

set -e

echo "💊 SaludApp Peru — Deploy"
echo "========================"

# 1. Check .env exists
if [ ! -f .env ]; then
    echo "❌ No existe .env. Creá uno: cp .env.example .env && nano .env"
    exit 1
fi

# 2. Verificar keys
if ! grep -q "GEMINI_API_KEY=AIza" .env 2>/dev/null; then
    echo "⚠️  GEMINI_API_KEY no configurada en .env"
    echo "   El OCR usará modo demo sin API key real."
fi

# 3. Construir y levantar
echo "🔨 Construyendo imagen Docker..."
docker compose build --no-cache

echo "🚀 Levantando contenedor..."
docker compose up -d

# 4. Esperar a que esté ready
echo "⏳ Esperando a que Streamlit arranque..."
sleep 5

# 5. Verificar
if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ SaludApp corriendo en http://localhost:8501"
    echo ""
    echo "📋 Logs: docker compose logs -f"
    echo "🔄 Update: git pull && docker compose up -d --build"
    echo "🛑 Stop: docker compose down"
else
    echo "⚠️  No responde todavía. Revisá: docker compose logs"
fi
