#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   Trading Bot IA - Iniciando   ${NC}"
echo -e "${BLUE}================================${NC}"

# Detect local IP
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Check .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠ Arquivo .env não encontrado. Copiando template...${NC}"
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env" 2>/dev/null || true
fi

# Install backend dependencies
echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"
cd "$ROOT_DIR"
pip install -r requirements.txt -q

# Install frontend dependencies
echo -e "${YELLOW}📦 Instalando dependências Node...${NC}"
cd "$FRONTEND_DIR"
npm install --silent

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Encerrando serviços...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

# Start backend
echo -e "${GREEN}🚀 Iniciando backend...${NC}"
cd "$BACKEND_DIR"
python main.py &
BACKEND_PID=$!

sleep 3

# Start frontend
echo -e "${GREEN}🚀 Iniciando frontend...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

sleep 2

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}   Sistema iniciado com sucesso! ${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "  ${BLUE}Frontend (local):${NC}  http://localhost:5173"
echo -e "  ${BLUE}Frontend (rede):${NC}   http://${LOCAL_IP}:5173"
echo -e "  ${BLUE}Backend API:${NC}       http://localhost:8000"
echo -e "  ${BLUE}WebSocket:${NC}         ws://localhost:8765"
echo ""
echo -e "${YELLOW}Para acessar pelo celular na mesma rede Wi-Fi:${NC}"
echo -e "  Abra http://${LOCAL_IP}:5173 no navegador do celular"
echo ""
echo -e "Pressione ${RED}Ctrl+C${NC} para encerrar"

wait $BACKEND_PID $FRONTEND_PID
