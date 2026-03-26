"""
claude_agent.py — Claude Computer Use para Mac 1080p (sin Retina, escala 1x)

FIXES vs version anterior:
- Sin escala Retina (1920x1080 es 1:1, coordenadas exactas)
- Usa pyautogui en lugar de cliclick (mas confiable para clicks)
- Sonnet en lugar de Haiku (mucho mas preciso en UI)
- Screenshots comprimidos para reducir tokens y costo
- Delays inteligentes segun tipo de accion
"""

import base64
import subprocess
import time
from PIL import Image
import pyautogui
from io import BytesIO


import anthropic

from config import ANTHROPIC_API_KEY, SCREEN_WIDTH, SCREEN_HEIGHT, CLAUDE_MODEL


class ClaudeAgent:
    def __init__(self, ):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.tools = [
            {
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": SCREEN_WIDTH,
                "display_height_px": SCREEN_HEIGHT,
                "display_number": 1,
            }
        ]

    def _log(self, text: str):
        print(text)

    def _take_screenshot(self) -> str:
        """
        Toma screenshot, lo redimensiona a 1280x720 antes de enviarlo a Claude.
        Reduce tokens y costo ~4x sin perder precision para tareas de UI.
        """

        self._log("Screenshot tomada")
        subprocess.run(
            ["screencapture", "-x", "-m", "-t", "png", "/tmp/sc.png"],
            capture_output=True
        )
        # Redimensionar para ahorrar tokens
        img = Image.open("/tmp/sc.png")

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")

        return b64

    def _focus_away_from_terminal(self):
        """Quita foco de Terminal antes de enviar teclas."""
        script = '''
        tell application "System Events"
            set termApps to {"Terminal", "iTerm2", "iTerm"}
            set frontApp to name of first application process whose frontmost is true
            if termApps contains frontApp then
                set appList to name of every application process whose visible is true
                repeat with appName in appList
                    if termApps does not contain (appName as string) and appName is not "Dock" and appName is not "SystemUIServer" and appName is not "Finder" then
                        set frontmost of (first application process whose name is appName) to true
                        return
                    end if
                end repeat
                tell application "Finder" to activate
            end if
        end tell
        '''
        subprocess.run(["osascript", "-e", script], capture_output=True)
        time.sleep(0.3)

    def _click(self, x: int, y: int, double: bool = False, right: bool = False):
        """
        Click con pyautogui — mas confiable que cliclick en macOS moderno.
        Las coordenadas vienen escaladas desde 1280x720 a 1920x1080.
        """
        # Claude ve imagen de 1280x720, pantalla real es 1920x1080
        # Escalar coordenadas proporcionalmente
        real_x = int(x * (SCREEN_WIDTH / 1280))
        real_y = int(y * (SCREEN_HEIGHT / 720))

        pyautogui.moveTo(real_x, real_y, duration=0.1)
        time.sleep(0.05)
        if right:
            pyautogui.rightClick()
        elif double:
            pyautogui.doubleClick()
        else:
            pyautogui.click()

    def _send_key(self, keys: str):
        """Envia combinacion de teclas al sistema (no a la Terminal)."""
        self._focus_away_from_terminal()

        mod_map = {
            "cmd": "command down", "command": "command down", "super": "command down",
            "ctrl": "control down", "control": "control down",
            "alt": "option down", "option": "option down",
            "shift": "shift down",
        }
        key_code_map = {
            "return": 36, "enter": 36, "escape": 53, "esc": 53,
            "space": 49, "tab": 48, "delete": 51, "backspace": 51,
            "up": 126, "down": 125, "left": 123, "right": 124,
        }

        keys_lower = keys.lower().strip()

        if "+" in keys_lower:
            parts = keys_lower.split("+")
            main_key = parts[-1].strip()
            modifiers = [mod_map[p.strip()]
                         for p in parts[:-1] if p.strip() in mod_map]
            mod_str = ", ".join(modifiers)
            if main_key in key_code_map:
                kc = key_code_map[main_key]
                script = f'tell application "System Events" to key code {kc} using {{{mod_str}}}'
            else:
                script = f'tell application "System Events" to keystroke "{main_key}" using {{{mod_str}}}'
        elif keys_lower in key_code_map:
            script = f'tell application "System Events" to key code {key_code_map[keys_lower]}'
        else:
            script = f'tell application "System Events" to keystroke "{keys}"'

        subprocess.run(["osascript", "-e", script], capture_output=True)

    def _type_text(self, text: str):
        """Escribe texto en la app activa (no en Terminal)."""
        self._focus_away_from_terminal()
        time.sleep(0.15)
        pyautogui.typewrite(text, interval=0.04)

    def _execute_tool(self, tool_use) -> dict:
        action = tool_use.input.get("action")
        self._log(f"  → {self.dict_model_mapper(tool_use)}")

        if action == "screenshot":
            b64 = self._take_screenshot()
            return {
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": [{"type": "image", "source": {
                    "type": "base64", "media_type": "image/jpeg", "data": b64
                }}]
            }

        elif action == "left_click":
            x, y = tool_use.input.get("coordinate", [0, 0])
            self._click(x, y)
            time.sleep(0.2)

        elif action == "double_click":
            x, y = tool_use.input.get("coordinate", [0, 0])
            self._click(x, y, double=True)
            time.sleep(0.2)

        elif action == "right_click":
            x, y = tool_use.input.get("coordinate", [0, 0])
            self._click(x, y, right=True)
            time.sleep(0.2)

        elif action == "mouse_move":
            x, y = tool_use.input.get("coordinate", [0, 0])
            real_x = int(x * (SCREEN_WIDTH / 1280))
            real_y = int(y * (SCREEN_HEIGHT / 720))
            pyautogui.moveTo(real_x, real_y, duration=0.1)

        elif action == "key":
            self._send_key(tool_use.input.get("text", ""))
            time.sleep(0.2)

        elif action == "type":
            text = tool_use.input.get("text", "")
            self._focus_away_from_terminal()
            time.sleep(0.15)
            # pyautogui.typewrite no maneja bien Unicode, usar osascript para eso
            safe = text.replace('"', '\\"').replace("\\", "\\\\")
            subprocess.run(["osascript", "-e",
                            f'tell application "System Events" to keystroke "{safe}"'],
                           capture_output=True)

        elif action == "scroll":
            x, y = tool_use.input.get("coordinate", [0, 0])
            direction = tool_use.input.get("direction", "down")
            amount = tool_use.input.get("amount", 3)
            real_x = int(x * (SCREEN_WIDTH / 1280))
            real_y = int(y * (SCREEN_HEIGHT / 720))
            pyautogui.moveTo(real_x, real_y)
            scroll_amount = amount if direction == "up" else -amount
            pyautogui.scroll(scroll_amount)

        # Esperar a que la UI reaccione antes del proximo screenshot
        time.sleep(0.4)
        b64 = self._take_screenshot()
        return {
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": [{"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg", "data": b64
            }}]
        }

    def quitImageInContent(self, contents):
        list = []
        for index, element in enumerate(contents):
            if element["type"] != "image":
                list.append(element)
            if element["type"] == "tool_result":

                element["content"] = [
                    {"type": "text",
                        "text": "Click executed. (Image removed to save tokens)"}

                ]
                list.append(element)
        return list

    def filtrarMessages(self, messages):
        list = []
        for index, message in enumerate(messages):
            if message["role"] != "user":
                list.append(message)
            else:
                newContents = self.quitImageInContent(
                    message["content"]) if index == len(messages) - 1 else [message["content"]]

                message["content"] = newContents
                list.append(message)
        return list

    def dict_model_mapper(self, value):
        if hasattr(value, "model_dump"):
            return value.model_dump()
        elif not isinstance(value, dict):
            # Fallback manual por si acaso (acceder a __dict__)
            return getattr(value, "__dict__", value)
        else:
            return value

    def optimize_history(self, new_messages):
        """
        Conserva  el texto, pero elimina CUALQUIER imagen 
        que no esté en el último mensaje.
        """

        messages = self.dict_model_mapper(new_messages)

        if not messages:
            return messages

        # 1. Identificamos cuál es el último mensaje que contiene una imagen
        last_msg_with_image_idx = -1
        for i in range(len(messages) - 1, -1, -1):
            content = messages[i].get("content", [])
            if isinstance(content, list):
                if any(self.dict_model_mapper(item).get("type") == "image" for item in content):
                    last_msg_with_image_idx = i
                    break

        # 2. Creamos el nuevo historial optimizado
        optimized_messages = []
        for i, msg in enumerate(messages):
            new_msg = {"role": msg["role"], "content": []}

            # Si el contenido es un string simple, se queda igual
            if isinstance(msg["content"], str):
                new_msg["content"] = msg["content"]
            else:
                # Si es una lista de bloques (como tool_use o tool_result)
                for item in msg["content"]:
                    # ¿Es una imagen?
                    if self.dict_model_mapper(item).get("type") == "image":
                        # Solo la dejamos si es la ÚLTIMA del historial
                        if i == last_msg_with_image_idx:
                            new_msg["content"].append(item)
                        else:
                            # Si es vieja, la quitamos pero dejamos una nota
                            new_msg["content"].append({
                                "type": "text",
                                "text": "[Imagen antigua omitida]"
                            })
                    else:
                        # TODO lo que NO sea imagen (texto, tool_use, etc.) SE QUEDA
                        new_msg["content"].append(item)

            optimized_messages.append(new_msg)

        return optimized_messages

    def run(self, instruction: str):
        self._log(f"\nEjecutando: '{instruction}'")

        b64 = self._take_screenshot()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/jpeg", "data": b64
                    }},
                    {"type": "text", "text": instruction}
                ]
            }
        ]

        max_steps = 10
        for step in range(max_steps):

            newMessages = self.optimize_history(

                messages) if step != 0 else messages

            response = self.client.beta.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                tools=self.tools,
                messages=newMessages,
                betas=["computer-use-2025-01-24"],
                system=(
                    "Eres un agente que controla una Mac 1920x1080. "
                    "REGLAS ESTRICTAS para minimizar clicks y tokens:\n"
                    "1. NAVEGACION: Brave Browser es el navegador principal, casi siempre visible en el Dock. "
                    "Antes de abrir Brave, toma un screenshot y verifica: "
                    "si Brave ya esta abierto y tiene una pestana con el sitio deseado, simplemente haz click en esa pestana. "
                    "Si Brave esta abierto pero sin el sitio, abre nueva pestana con cmd+t y escribe la URL directamente. "
                    "Si Brave no esta abierto, clickea su icono en el Dock. Procura no usar Spotlight para abrir Brave. "
                    "2. EFICIENCIA: Usa siempre el camino con menos clicks. "
                    "Si puedes escribir una URL directamente, hazlo en lugar de buscar. "
                    "Si un elemento es clickeable, clickealo directamente sin hacer hover primero. "
                    "3. SCREENSHOTS: Solo toma screenshot cuando necesites verificar el estado actual. "
                    "No tomes screenshots redundantes entre acciones consecutivas obvias (ej: abrir pestana -> escribir URL). "
                    "4. COORDENADAS: Las imagenes son 1280x720. Apunta siempre al CENTRO del elemento. "
                    "5. COMPLETAR: Una vez logrado el objetivo, detente. No hagas acciones adicionales."
                )
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        self._log(f"✓ {block.text}")

                break

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self._execute_tool(block)
                    tool_results.append(result)

            if not tool_results:
                break

            messages.append({"role": "assistant", "content": response.content})

            messages.append(
                {"role": "user", "content": tool_results})

            self._log("Tarea completada.\n")

    def prepare_messages_for_api(self, full_history: dict):
        """
        Conserva todo el texto (el hilo de la conversación), 
        pero elimina los datos base64 de los screenshots antiguos.
        Solo deja el ÚLTIMO screenshot para que Claude vea el presente.
        """
        cleaned_messages = []

        # Encontramos el índice del último mensaje que tiene una imagen
        last_image_idx = -1
        for i, msg in enumerate(full_history):
            if isinstance(msg["content"], list):
                if any(item.get("type") == "image" for item in msg["content"]):
                    last_image_idx = i

        for i, msg in enumerate(full_history):
            # Hacemos una copia profunda para no alterar el historial original si lo usas para logs
            new_msg = {"role": msg["role"], "content": []}

            if isinstance(msg["content"], str):
                new_msg["content"] = msg["content"]
            else:
                for item in msg["content"]:
                    if item["type"] == "image":
                        # ¿Es el último screenshot? Lo dejamos.
                        if i == last_image_idx:
                            new_msg["content"].append(item)
                        else:
                            # ¿Es un screenshot viejo? Lo convertimos a texto simple.
                            new_msg["content"].append({
                                "type": "text",
                                "text": "[Screenshot anterior eliminado para ahorrar tokens]"
                            })
                    else:
                        # Si es texto o tool_use, se queda igual
                        new_msg["content"].append(item)

            cleaned_messages.append(new_msg)

        return cleaned_messages
