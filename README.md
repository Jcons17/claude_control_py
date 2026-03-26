# 🎙️ Voice Computer Use — Mac M4

Controla tu Mac con voz usando Whisper nativo + Claude Computer Use.

## Estructura

```
voice-computer-use/
├── config.py         ← EMPIEZA AQUÍ: pon tu API key y keyword
├── main.py           ← Loop principal
├── transcriber.py    ← Whisper en Apple Silicon (mlx-whisper)
├── claude_agent.py   ← Claude Computer Use
├── launch.sh         ← Doble clic para iniciar todo
└── requirements.txt
```

## Setup (solo una vez)

### 1. Pon tu API Key y keyword en config.py
```python
ANTHROPIC_API_KEY = "sk-ant-TU_KEY_AQUI"
KEYWORD = "oye claude"   # ← la que quieras
```

### 2. Instala Homebrew (si no lo tienes)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Dale permisos al script
```bash
chmod +x launch.sh
```

### 4. Dale permisos de Accesibilidad a Terminal
- Ve a: Preferencias del Sistema → Privacidad y Seguridad → Accesibilidad
- Agrega Terminal.app a la lista ✅

### 5. Haz doble clic en launch.sh
El script instala todo automáticamente la primera vez.

---

## Uso

| Acción | Qué hace |
|--------|----------|
| Doble clic en `launch.sh` | Inicia el sistema |
| Presiona ENTER | Enciende el micrófono |
| Habla | Graba tu voz |
| Presiona ENTER | Para la grabación y transcribe |
| `"[KEYWORD] abre YouTube"` | Claude ejecuta la acción |
| Sin keyword | El texto se ignora |
| `"cancelar escucha"` | Apaga el sistema |

## Ejemplos de comandos

```
"oye claude abre YouTube y busca videos de Veritasium"
"oye claude abre una nueva pestaña en el navegador"
"oye claude pon música en Spotify"
"oye claude toma un screenshot y guárdalo en el escritorio"
```

## Permisos necesarios en macOS

- **Accesibilidad** → Terminal (para controlar el mouse/teclado)
- **Micrófono** → Terminal (para grabar voz)
- **Grabación de pantalla** → Terminal (para los screenshots de Computer Use)
