/**
 * SaludApp Peru — WhatsApp Gateway con Baileys
 *
 * PARA USAR:
 *   1. Asegurate que FastAPI esté corriendo: uvicorn backend.app.main:app --port 8000
 *   2. node baileys_gateway.js
 *   3. Escanea el QR con tu WhatsApp (Config > Linked Devices > Link a Device)
 *   4. ¡Listo! Mandá un mensaje o foto a tu propio WhatsApp y el bot responde.
 */

const { makeWASocket, useMultiFileAuthState, DisconnectReason, downloadMediaMessage, getContentType } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const http = require('http');
const qrcode = require('qrcode-terminal');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

// Whitelist: números permitidos (sin +, sin @). Ej: "5491112345678,5491187654321"
// Si está vacío, responde a TODOS (no recomendado con número personal)
const ALLOWED_NUMBERS = process.env.ALLOWED_NUMBERS
    ? new Set(process.env.ALLOWED_NUMBERS.split(',').map(n => n.trim()))
    : null;


const botSentIds = new Set();
let ownLid = null;

// ── Anti-spam con warnings ────────────────────────────────────────────────────
const userActivity = new Map(); // jid → { msgs: [], warnings: 0, blocked: false }
const WARN_THRESHOLD  = 15; // msgs en 60s → warning
const BLOCK_THRESHOLD = 25; // msgs en 60s después de warning → block temporal (10 min)
const BLOCK_DURATION  = 10 * 60 * 1000; // 10 minutos

function checkSpam(jid) {
    const now = Date.now();
    if (!userActivity.has(jid)) userActivity.set(jid, { msgs: [], warnings: 0, blocked: false, blockedUntil: 0 });
    const u = userActivity.get(jid);

    // Verificar si sigue bloqueado
    if (u.blocked && now < u.blockedUntil) return 'blocked';
    if (u.blocked && now >= u.blockedUntil) { u.blocked = false; u.warnings = 0; }

    // Limpiar mensajes fuera de ventana 60s
    u.msgs = u.msgs.filter(t => now - t < 60000);
    u.msgs.push(now);

    if (u.msgs.length >= BLOCK_THRESHOLD && u.warnings > 0) {
        u.blocked = true; u.blockedUntil = now + BLOCK_DURATION;
        return 'block';
    }
    if (u.msgs.length >= WARN_THRESHOLD && u.warnings === 0) {
        u.warnings++;
        return 'warn';
    }
    return 'ok';
}

function isAllowed(jid) {
    if (jid.endsWith('@g.us')) return false;  // grupos → siempre bloqueado
    if (jid.endsWith('@lid')) {
        // Sin whitelist → permitir TODOS los LID (usuarios reales en multi-device)
        // Con whitelist → solo el propio LID (modo demo personal)
        return !ALLOWED_NUMBERS || jid === ownLid;
    }
    if (!ALLOWED_NUMBERS) return true;
    const number = jid.split('@')[0].split(':')[0].trim();
    return ALLOWED_NUMBERS.has(number);
}

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('whatsapp_auth');

    const sock = makeWASocket({
        auth: state,
        browser: ['SaludApp Peru', 'Chrome', '1.0'],
    });

    sock.ev.on('creds.update', saveCreds);

    // Manejar mensajes entrantes
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        console.log(`[DEBUG] messages.upsert type=${type} count=${messages.length} jids=${messages.map(m=>m.key?.remoteJid).join(',')}`);
        if (type !== 'notify' && type !== 'append') return;

        for (const msg of messages) {
            if (!msg.message) continue;
            // Saltear mensajes enviados por el bot (evitar loop)
            if (msg.key.fromMe && botSentIds.has(msg.key.id)) continue;
            // Saltear otros fromMe que no sean del usuario whitelisted
            if (msg.key.fromMe && !isAllowed(msg.key.remoteJid)) continue;

            const from = msg.key.remoteJid;

            // Grupos → siempre ignorar
            if (!isAllowed(from)) {
                console.log(`⏭️  Ignorado (grupo/no permitido): ${from}`);
                continue;
            }

            // Anti-spam
            const spamStatus = checkSpam(from);
            if (spamStatus === 'blocked') {
                console.log(`🚫 Bloqueado temporalmente: ${from}`);
                continue;
            }
            if (spamStatus === 'warn') {
                await sock.sendMessage(from, {
                    text: '⚠️ Estás enviando muchos mensajes. Por favor esperá un momento o te bloquearemos temporalmente.'
                });
                console.log(`⚠️ Warning enviado a: ${from}`);
            }
            if (spamStatus === 'block') {
                await sock.sendMessage(from, {
                    text: '🚫 Fuiste bloqueado temporalmente por 10 minutos por exceso de mensajes.'
                });
                console.log(`🚫 Bloqueado: ${from}`);
                continue;
            }

            const sender = msg.pushName || 'Paciente';
            console.log(`\n📲 Mensaje de ${sender} (${from})`);

            let text = '';
            let imageBase64 = null;
            let imageType = 'jpeg';
            let audioBase64 = null;

            // Extraer texto
            const msgType = getContentType(msg.message);
            console.log(`[DEBUG] msgType=${msgType} keys=${Object.keys(msg.message).join(',')}`);
            console.log(`[DEBUG] msg.message=`, JSON.stringify(msg.message).slice(0, 300));
            const conv = msg.message.conversation;
            const extText = msg.message.extendedTextMessage?.text;
            const ephText = msg.message.ephemeralMessage?.message?.conversation
                         || msg.message.ephemeralMessage?.message?.extendedTextMessage?.text;
            text = conv || extText || ephText || '';
            console.log(`[DEBUG] text extracted: "${text}"`);

            // Extraer imagen
            const imageMsg = msg.message.imageMessage;
            if (imageMsg) {
                console.log('📸 Imagen recibida, descargando...');
                try {
                    const buffer = await downloadMediaMessage(msg, 'buffer', {});
                    imageBase64 = buffer.toString('base64');
                    imageType = imageMsg.mimetype?.split('/')[1] || 'jpeg';
                    console.log(`   ✅ ${buffer.length} bytes, tipo: ${imageType}`);
                    if (!text) text = '[Foto de receta médica]';
                } catch (e) {
                    console.error('   ❌ Error descargando imagen:', e.message);
                }
            }

            // Extraer audio / nota de voz (ptt = push-to-talk)
            let audioDurationSeconds = 0;
            const audioMsg = msg.message.audioMessage || msg.message.pttMessage;
            if (audioMsg) {
                audioDurationSeconds = audioMsg.seconds || 0;
                console.log(`🎤 Audio recibido (${audioDurationSeconds}s), descargando...`);
                try {
                    const buffer = await downloadMediaMessage(msg, 'buffer', {});
                    audioBase64 = buffer.toString('base64');
                    console.log(`   ✅ ${buffer.length} bytes de audio`);
                } catch (e) {
                    console.error('   ❌ Error descargando audio:', e.message);
                }
            }

            // Enviar a FastAPI
            if (text || imageBase64 || audioBase64) {
                // Texto → "escribiendo..." nativo (desaparece solo)
                // Audio/imagen → mensaje visible porque tarda más
                if (audioBase64 || imageBase64) {
                    const slowMsg = audioBase64 ? '🎤 *_Escuchando tu audio..._*' : '⏳ *_Procesando tu receta..._*';
                    const typingSent = await sock.sendMessage(from, { text: slowMsg });
                    if (typingSent?.key?.id) { botSentIds.add(typingSent.key.id); setTimeout(() => botSentIds.delete(typingSent.key.id), 60000); }
                } else {
                    await sock.sendPresenceUpdate('composing', from);
                }

                const payload = JSON.stringify({
                    from_number: from,
                    text: text || null,
                    image_base64: imageBase64,
                    image_type: imageType,
                    audio_base64: audioBase64,
                    audio_duration_seconds: audioDurationSeconds,
                });

                try {
                    const response = await httpRequest('/whatsapp/webhook', payload);
                    const data = JSON.parse(response);

                    if (data.response) {
                        const sent = await sock.sendMessage(from, { text: data.response });
                        if (sent?.key?.id) { botSentIds.add(sent.key.id); setTimeout(() => botSentIds.delete(sent.key.id), 60000); }
                        console.log('✅ Respuesta enviada');
                    }
                } catch (e) {
                    console.error('❌ Error:', e.message);
                    const errSent = await sock.sendMessage(from, {
                        text: '❌ Lo siento, hubo un error. ¿Probás de nuevo?'
                    });
                    if (errSent?.key?.id) { botSentIds.add(errSent.key.id); setTimeout(() => botSentIds.delete(errSent.key.id), 60000); }
                }
            }
        }
    });

    // Manejar conexión
    sock.ev.on('connection.update', ({ connection, lastDisconnect, qr }) => {
        if (qr) {
            console.log('\n📱 ESCANEÁ ESTE QR CON WHATSAPP:');
            console.log('   WhatsApp > Config > Linked Devices > Link a Device\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            console.log('⚠️ Conexión cerrada. Reconectando:', shouldReconnect);
            if (shouldReconnect) {
                setTimeout(startBot, 3000);
            } else {
                console.log('❌ Sesión cerrada. Borrá whatsapp_auth/ y reiniciá.');
            }
        } else if (connection === 'open') {
            // Guardar propio LID para permitir "mensaje a vos mismo"
            const lid = sock.user?.lid || sock.authState?.creds?.me?.lid;
            if (lid) ownLid = lid.split(':')[0] + '@lid';
            console.log(`\n✅ ¡WhatsApp conectado! ownLid=${ownLid}`);
            console.log('   Mandá un mensaje o foto de receta a este número.\n');
        }
    });
}

function httpRequest(path, body) {
    const url = new URL(FASTAPI_URL);
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: url.hostname,
            port: url.port || 8000,
            path: path,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body),
            },
            timeout: 30000,
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => resolve(data));
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
        req.write(body);
        req.end();
    });
}

console.log('💊 SaludApp Peru — WhatsApp Gateway');
console.log('==================================\n');
console.log('⚠️  Asegurate que FastAPI esté corriendo:');
console.log('   uvicorn backend.app.main:app --port 8000\n');

startBot().catch(console.error);
