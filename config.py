# ============================================================
#  CONFIGURACIÓN — edita estas variables antes de correr
# ============================================================

# Tu API Key de Anthropic
ANTHROPIC_API_KEY = "sk---"

# Palabra clave que activa Computer Use
# Ejemplos: "oye claude", "ejecuta", "computadora", "hey mac"
# Modelo de Claude a usar
CLAUDE_MODEL = "claude-opus-4-5"

# Modelo de Whisper (opciones: "tiny", "base", "small", "medium", "large")
# Para Mac M4 se recomienda "medium" o "large" — son rápidos gracias al chip
WHISPER_MODEL = "large"

# Idioma de escucha (None = autodetectar, o pon "es" para español, "en" para inglés)
WHISPER_LANGUAGE = "es"

# Segundos de silencio para considerar que terminaste de hablar
SILENCE_THRESHOLD_SECONDS = 1.5

# Resolución de pantalla de tu Mac (se usa para Computer Use)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
