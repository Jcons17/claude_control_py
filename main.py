"""
main.py — Loop principal del sistema de voz + Computer Use.

FLUJO:
  1. Corres el .sh → se inicializa todo
  2. El micrófono queda en espera
  3. Presionas ENTER (o el .sh lo activa) → graba tu voz
  4. Presionas ENTER de nuevo → para la grabación y transcribe
  5. Si el texto empieza con KEYWORD → Claude ejecuta la acción en pantalla
  6. Si no tiene keyword → se ignora (puedes adaptarlo para dictado)
  7. Di "cancelar escucha" o "detener" como keyword para salir
"""

import sys
from transcriber import Transcriber
from claude_agent import ClaudeAgent


# Palabras que apagan el sistema completamente
STOP_WORDS = ["cancelar escucha", "detener sistema", "apagar claude", "stop"]


def normalize(text: str) -> str:
    """Convierte a minúsculas y quita espacios extra para comparar."""
    return text.lower().strip()


def main():
    print("=" * 55)
    print("  🎙️  Voice Computer Use — Mac M4")
    print("=" * 55)
    print(f"  Para salir     : di '{STOP_WORDS[0]}' o Ctrl+C")
    print("=" * 55)
    print()

    transcriber = Transcriber()
    agent = ClaudeAgent()

    running = True

    try:
        while running:
            print("⏳ Listo. Presiona ENTER para hablar (Ctrl+C para salir)...")
            input()  # Espera que el usuario presione Enter

            # --- GRABA ---
            transcriber.start_listening()
            print("🔴 Grabando... presiona ENTER para detener")
            input()

            # --- TRANSCRIBE ---
            text = transcriber.stop_and_transcribe()

            if not text:
                print("⚠️  No se detectó audio. Intenta de nuevo.\n")
                continue

            # --- CHECA SI ES COMANDO DE APAGADO ---
            for stop_word in STOP_WORDS:
                if stop_word in normalize(text):
                    print("👋 Apagando Voice Computer Use. ¡Hasta luego!")
                    running = False
                    break

            if not running:
                break

            command = text

            if command:
                print(f"🚀 Comando detectado: '{command}'")
                agent.run(command)

    except KeyboardInterrupt:
        print("\n👋 Interrumpido por el usuario. ¡Hasta luego!")
        sys.exit(0)


if __name__ == "__main__":
    main()
