"""
WhatsApp Bridge usando Baileys (via whiskeysockets/baileys)

Requisitos:
  npm install -g @whiskeysockets/baileys
  pip install websockets

Flow:
  1. Node.js corre Baileys → escanea QR con tu WhatsApp
  2. Baileys recibe mensajes → reenvía a FastAPI (/whatsapp/webhook)
  3. FastAPI procesa → responde → Baileys envía respuesta al chat

Para demo EN VIVO: este script inicia Baileys + servidor WebSocket.
Alternativa simple: usar la simulación Streamlit (YA funciona, mismo resultado).
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

BAILEYS_SCRIPT = """
const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const http = require('http');

async function start() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,  // Escanea este QR con WhatsApp
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('messages.upsert', async ({ messages }) => {
        for (const msg of messages) {
            if (!msg.message || msg.key.fromMe) continue;

            const from = msg.key.remoteJid;
            let text = '';
            let imageBase64 = '';

            // Texto
            const conversation = msg.message.conversation || msg.message.extendedTextMessage?.text;
            if (conversation) text = conversation;

            // Imagen
            const imageMsg = msg.message.imageMessage;
            if (imageMsg) {
                // Descargar imagen
                const stream = await require('stream').Readable.from(sock.downloadMediaMessage(msg));
                const chunks = [];
                for await (const chunk of stream) chunks.push(chunk);
                imageBase64 = Buffer.concat(chunks).toString('base64');
                text = text || '[Imagen recibida]';
            }

            // Enviar a FastAPI
            if (text || imageBase64) {
                try {
                    const payload = JSON.stringify({
                        from_number: from,
                        text: text || null,
                        image_base64: imageBase64 || null,
                    });

                    const req = http.request({
                        hostname: 'localhost', port: 8000,
                        path: '/whatsapp/webhook', method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                    });
                    req.write(payload);
                    req.end();

                    // Esperar respuesta de FastAPI
                    const resp = await new Promise((resolve, reject) => {
                        req.on('response', (res) => {
                            let data = '';
                            res.on('data', c => data += c);
                            res.on('end', () => resolve(JSON.parse(data)));
                        });
                        req.on('error', reject);
                    });

                    // Enviar respuesta al chat de WhatsApp
                    await sock.sendMessage(from, { text: resp.response });
                    console.log('Respuesta enviada a', from);
                } catch (e) {
                    console.error('Error:', e.message);
                }
            }
        }
    });

    sock.ev.on('connection.update', ({ connection, lastDisconnect }) => {
        if (connection === 'close') {
            const shouldReconnect = (new Boom(lastDisconnect?.error))?.output?.statusCode !== DisconnectReason.loggedOut;
            if (shouldReconnect) start();
        } else if (connection === 'open') {
            console.log('✅ WhatsApp conectado!');
        }
    });
}

start();
"""


def generate_baileys_script():
    """Escribe el script de Baileys a disco."""
    path = Path(__file__).parent / "baileys_gateway.js"
    path.write_text(BAILEYS_SCRIPT)
    print(f"✅ Script Baileys: {path}")
    return path


def start_whatsapp_bridge():
    """
    Inicia el bridge WhatsApp.

    1. Asegura que FastAPI esté corriendo en :8000
    2. Inicia Baileys → muestra QR
    3. Escanea QR con tu WhatsApp personal
    4. Listo: mensajes de WhatsApp → FastAPI → respuesta → WhatsApp
    """
    script = generate_baileys_script()

    print("=" * 60)
    print("🔌 Iniciando WhatsApp Bridge (Baileys)")
    print("=" * 60)
    print()
    print("1. Asegurate que FastAPI esté corriendo:")
    print("   uvicorn backend.app.main:app --port 8000")
    print()
    print("2. Instalá dependencias Node.js:")
    print("   npm install @whiskeysockets/baileys @hapi/boom")
    print()
    print("3. Iniciando Baileys...")
    print("   (Escanea el QR con WhatsApp en tu celular)")
    print()

    subprocess.run(["node", str(script)], cwd=Path(__file__).parent)


if __name__ == "__main__":
    start_whatsapp_bridge()
