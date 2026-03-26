"""
transcriber.py — Transcripción de voz con Whisper nativo en Apple Silicon (M4)
Usa mlx-whisper que corre directamente en el chip, sin necesidad de GPU externa.
"""

import queue
import threading
import tempfile
import os
import numpy as np
import sounddevice as sd
import soundfile as sf
import mlx_whisper
from config import WHISPER_MODEL, WHISPER_LANGUAGE, SILENCE_THRESHOLD_SECONDS


class Transcriber:
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.recording = False
        self.audio_queue = queue.Queue()
        self._audio_buffer = []
        self._stream = None

        print(f"🧠 Cargando Whisper modelo '{WHISPER_MODEL}' en Apple Silicon...")
        # mlx_whisper carga el modelo en el chip M4 automáticamente
        self._model_name = f"mlx-community/whisper-{WHISPER_MODEL}-mlx"
        print("✅ Whisper listo.")

    def _audio_callback(self, indata, frames, time, status):
        """Callback que recibe audio del micrófono en tiempo real."""
        if self.recording:
            self._audio_buffer.append(indata.copy())

    def start_listening(self):
        """Abre el stream del micrófono."""
        self._audio_buffer = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._audio_callback
        )
        self._stream.start()
        self.recording = True
        print("🎙️  Micrófono encendido — habla ahora")

    def stop_and_transcribe(self) -> str:
        """Detiene la grabación y devuelve el texto transcrito."""
        self.recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if not self._audio_buffer:
            return ""

        # Unir todos los chunks de audio
        audio_data = np.concatenate(self._audio_buffer, axis=0).flatten()

        # Guardar en archivo temporal .wav
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            sf.write(tmp_path, audio_data, self.sample_rate)

        try:
            print("⚙️  Transcribiendo...")
            result = mlx_whisper.transcribe(
                tmp_path,
                path_or_hf_repo=self._model_name,
                language=WHISPER_LANGUAGE,
                verbose=False
            )
            text = result.get("text", "").strip()
            print(f"📝 Transcripción: '{text}'")
            return text
        finally:
            os.unlink(tmp_path)
