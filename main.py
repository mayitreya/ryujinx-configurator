# Full transparency here, the design of the UI is made by me, but enhanced by AI (animations, colors, icons, and such) because I'm a terrible designer
# Also a lot of the "boring" and "menial" stuff was vibe coded too because I can't be bothered to write all of that manually

# (to be clear, yes, this is me taking a stance against excessive generative AI usage because it makes you stupid and a bad programmer :D)

# The logic behind understanding the way the Config.json file and Ryujinx interact with each other was all done by me
# Also, I want to vent some frustrations here because this tripped me up for a good two hours
# Why the HELL does Ryujinx not just use standard SDL controller GUIDs??? I had to reverse engineer how the GUIDs were being generated
# In other words, it uses big endian for part of it, and little endian for another part of the same GUID?? Like it doesn't make any sense
# This app will convert between STANDARD (gosh imagine using a standard that's documented? couldn't be Ryujinx apparently) SDL controller GUIDs and Ryujinx's wack big-little-endian slop

# And lastly, to whomever is reading this, I'm sorry for the monolithic code I've written here
# It's definitely a good idea to turn this file into a more modular approach, so that the same UI could be used for other emulators :)
# That's a "later" task though...
# Good luck soldier o7

import os
import sys
import json

if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(SCRIPT_DIR, "Config.json")
BACKUP_FILE = os.path.join(SCRIPT_DIR, "Config.json.bak")
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "rct_settings.json")

# Whether SDL HIDAPI is on decides which GUID a pad gets. The "right" answer depends on the Ryujinx build the user runs against: Flatpak Ryujinx on Steam
# Deck enables HIDAPI by default, native Ryujinx on most Linux distros does not. We can't infer which one, so it's a user-controlled toggle persisted in
# SETTINGS_FILE. Default off = matches stock pygame behaviour, which agrees with native Ryujinx. Toggle via [H] in the diagnostics overlay.
_HIDAPI_KEYS = (
    "SDL_JOYSTICK_HIDAPI",
    "SDL_JOYSTICK_HIDAPI_SWITCH",
    "SDL_JOYSTICK_HIDAPI_PS4",
    "SDL_JOYSTICK_HIDAPI_PS5",
    "SDL_JOYSTICK_HIDAPI_XBOX",
    "SDL_JOYSTICK_HIDAPI_XBOX_360",
    "SDL_JOYSTICK_HIDAPI_XBOX_ONE",
    "SDL_JOYSTICK_HIDAPI_GAMECUBE",
    "SDL_JOYSTICK_HIDAPI_JOYCON",
    "SDL_JOYSTICK_HIDAPI_STADIA",
    "SDL_JOYSTICK_HIDAPI_LUNA",
)
try:
    with open(SETTINGS_FILE, 'r') as _f:
        HIDAPI_ENABLED = bool(json.load(_f).get("hidapi", False))
except Exception:
    HIDAPI_ENABLED = False
for _k in _HIDAPI_KEYS:
    os.environ[_k] = "1" if HIDAPI_ENABLED else "0"

import pygame
import copy
import shutil
import math
MAX_PLAYERS = 8

THEME = {
    "bg": (22, 27, 34),
    "panel": (40, 46, 56),
    "panel_sel": (55, 62, 75),
    "text": (230, 232, 235),
    "text_dim": (140, 145, 155),
    "accent": (88, 166, 255),
    "green": (76, 175, 80),
    "warning": (255, 193, 7),
    "header_bg": (18, 20, 25),
    "divider": (60, 65, 75),
    "shadow": (0, 0, 0)
}

DROPDOWN_MAP = [
    ("A", "A"), ("B", "B"), ("X", "X"), ("Y", "Y"),
    ("+", "Plus"), ("-", "Minus"),
    ("Up (dpad)", "DpadUp"), ("Down (dpad)", "DpadDown"), 
    ("Left (dpad)", "DpadLeft"), ("Right (dpad)", "DpadRight"),
    ("Left Stick (Motion)", "Left"), ("Right Stick (Motion)", "Right"),
    ("L Stick Button", "LeftStick"), ("R Stick Button", "RightStick"),
    ("Left Shoulder", "LeftShoulder"), ("Right Shoulder", "RightShoulder"),
    ("Left Trigger", "LeftTrigger"), ("Right Trigger", "RightTrigger"),
    ("Guide", "Guide"),
    ("Paddle 1", "Paddle1"), ("Paddle 2", "Paddle2"), 
    ("Paddle 3", "Paddle3"), ("Paddle 4", "Paddle4"),
    ("Unbound", "Unbound")
]

TARGETS_GAMEPAD = [
    ("Action: A (East)", "button_a"), ("Action: B (South)", "button_b"), 
    ("Action: X (North)", "button_x"), ("Action: Y (West)", "button_y"),
    ("Action: +", "button_plus"), ("Action: -", "button_minus"),
    ("Action: L Shoulder", "button_l"), ("Action: R Shoulder", "button_r"), 
    ("Action: ZL Trigger", "button_zl"), ("Action: ZR Trigger", "button_zr"),
    ("Action: L Stick Click", "stick_button_left"), 
    ("Action: R Stick Click", "stick_button_right"),
    ("Action: D-Pad Up", "dpad_up"), ("Action: D-Pad Down", "dpad_down"), 
    ("Action: D-Pad Left", "dpad_left"), ("Action: D-Pad Right", "dpad_right"),
    ("Stick: Left Motion", "joystick_left"),
    ("Stick: Right Motion", "joystick_right")
]

TARGETS_KEYBOARD = [
    ("Key: A", "button_a"), ("Key: B", "button_b"), 
    ("Key: X", "button_x"), ("Key: Y", "button_y"),
    ("Key: +", "button_plus"), ("Key: -", "button_minus"),
    ("Key: L Shoulder", "button_l"), ("Key: R Shoulder", "button_r"), 
    ("Key: ZL Trigger", "button_zl"), ("Key: ZR Trigger", "button_zr"),
    ("Key: L Stick Btn", "stick_button_left"), 
    ("Key: R Stick Btn", "stick_button_right"),
    ("Key: D-Pad Up", "dpad_up"), ("Key: D-Pad Down", "dpad_down"), 
    ("Key: D-Pad Left", "dpad_left"), ("Key: D-Pad Right", "dpad_right"),
    ("L Stick: Up", "lstick_up"), ("L Stick: Down", "lstick_down"),
    ("L Stick: Left", "lstick_left"), ("L Stick: Right", "lstick_right"),
    ("R Stick: Up", "rstick_up"), ("R Stick: Down", "rstick_down"),
    ("R Stick: Left", "rstick_left"), ("R Stick: Right", "rstick_right")
]

KEY_TRANSLATION = {
    "return": "Enter", "escape": "Escape", "backspace": "BackSpace",
    "tab": "Tab", "space": "Space", "delete": "Delete",
    "up": "Up", "down": "Down", "left": "Left", "right": "Right",
    "left shift": "ShiftLeft", "right shift": "ShiftRight",
    "left ctrl": "ControlLeft", "right ctrl": "ControlRight",
    "left alt": "AltLeft", "right alt": "AltRight",
    "`": "Tilde", "backquote": "Tilde", "-": "Minus", "=": "Plus",
    "[": "BracketLeft", "]": "BracketRight", ";": "Semicolon", "'": "Quote",
    ",": "Comma", ".": "Period", "/": "Slash", "\\": "BackSlash",
}

TEMPLATE_BASE = {
    "version": 1,
    "backend": "GamepadSDL2",
    "controller_type": "ProController",
    "deadzone_left": 0.1, "deadzone_right": 0.1,
    "range_left": 1, "range_right": 1,
    "trigger_threshold": 0.5,
    "motion": { "motion_backend": "GamepadDriver", "sensitivity": 100, "gyro_deadzone": 1, "enable_motion": True },
    "rumble": { "strong_rumble": 1, "weak_rumble": 1, "enable_rumble": True },
    "led": { "enable_led": False, "turn_off_led": False, "use_rainbow": False, "led_color": 0 },
    "left_joycon": { 
        "button_minus": "Unbound", "button_l": "Unbound", "button_zl": "Unbound", 
        "button_sl": "Unbound", "button_sr": "Unbound",
        "dpad_up": "Unbound", "dpad_down": "Unbound", "dpad_left": "Unbound", "dpad_right": "Unbound" 
    }, 
    "right_joycon": { 
        "button_plus": "Unbound", "button_r": "Unbound", "button_zr": "Unbound", 
        "button_sl": "Unbound", "button_sr": "Unbound",
        "button_a": "Unbound", "button_b": "Unbound", "button_x": "Unbound", "button_y": "Unbound" 
    },
    "left_joycon_stick": { 
        "joystick": "Left", "invert_stick_x": False, "invert_stick_y": False, "rotate90_cw": False, 
        "stick_button": "Unbound", "stick_up": "Unbound", "stick_down": "Unbound", "stick_left": "Unbound", "stick_right": "Unbound"
    },
    "right_joycon_stick": { 
        "joystick": "Right", "invert_stick_x": False, "invert_stick_y": False, "rotate90_cw": False, 
        "stick_button": "Unbound", "stick_up": "Unbound", "stick_down": "Unbound", "stick_left": "Unbound", "stick_right": "Unbound"
    }
}

# So you can hold your buttons down n stuff
class InputRepeater:
    def __init__(self):
        self.last_move_time = 0
        self.initial_delay = 0.4
        self.repeat_rate = 0.08
        self.held_dir = None
        self.hold_start_time = 0

    def check(self, direction):
        now = pygame.time.get_ticks() / 1000.0
        if direction != self.held_dir:
            self.held_dir = direction
            self.hold_start_time = now
            self.last_move_time = now
            return True if direction else False
        
        if direction and (now - self.hold_start_time > self.initial_delay):
            if now - self.last_move_time > self.repeat_rate:
                self.last_move_time = now
                return True
        return False

    def reset(self):
        self.held_dir = None

class App:
    # Vibe coded lmfao
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        info = pygame.display.Info()
        self.W, self.H = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.FULLSCREEN)

        # Scale layout from a 1920x1080 reference, shrink-only so big displays
        # render at native sizes and small displays (Steam Deck 1280x800) fit.
        self.scale = min(self.W / 1920.0, self.H / 1080.0, 1.0)

        self.font_title = pygame.font.SysFont("segoe ui", self.s(52), bold=True)
        self.font_lg = pygame.font.SysFont("segoe ui", self.s(38))
        self.font_md = pygame.font.SysFont("segoe ui", self.s(30))
        self.font_sm = pygame.font.SysFont("segoe ui", self.s(24))
        
        self.refresh_joysticks()

        self.status_msg = ""
        self.status_color = THEME["green"]
        self.status_until = 0
        self.load_failed = False
        self.show_diag = False
        self.config_data = self.load_json()

        self.state = "MENU"
        self.selected_slot = 0
        self.selected_map_index = 0
        self.dropdown_index = 0
        self.dropdown_offset = 0
        self.last_nav_time = 0
        self.nav_delay = 0.12
        self.active_joy = None
        self.active_device_type = None 
        self.current_config = None
        self.current_target_list = []
        
        self.animation_time = 0
        self.transition_timer = 0 
        self.input_repeater = InputRepeater()
        self.cursor_rect = pygame.Rect(0,0,0,0)
        self.target_cursor_rect = pygame.Rect(0,0,0,0)

    def refresh_joysticks(self):
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.joysticks: j.init()

        self.controllers = {}
        try:
            from pygame._sdl2 import controller as sdl_controller
            if not sdl_controller.get_init():
                sdl_controller.init()
            for j in self.joysticks:
                try:
                    c = sdl_controller.Controller.from_joystick(j)
                    c.init()
                    self.controllers[j.get_instance_id()] = c
                except Exception:
                    pass
        except Exception:
            pass

    @property
    def controller_ids(self):
        return set(self.controllers.keys())

    def device_name(self, joy):

        c = self.controllers.get(joy.get_instance_id())
        if c is not None:
            try:
                if c.name: return c.name
            except Exception:
                pass
        return joy.get_name()

    def find_joystick(self, instance_id):
        for j in self.joysticks:
            if j.get_instance_id() == instance_id: return j
        return None

    def pick_gamepad(self, instance_id):
        joy = self.find_joystick(instance_id)
        if joy is None:
            self.refresh_joysticks()
            joy = self.find_joystick(instance_id)
        if joy is not None:
            self.active_device_type = "gamepad"
            self.active_joy = joy
            self.current_config = self.setup_config_for_player()
            self.change_state("MAPPING")

    def s(self, n):
        return max(1, int(round(n * self.scale)))

    def change_state(self, new_state):
        self.state = new_state
        self.transition_timer = pygame.time.get_ticks() + 300 
        self.input_repeater.reset()

    def input_locked(self):
        return pygame.time.get_ticks() < self.transition_timer

    def set_status(self, msg, color=None, secs=3.0):
        self.status_msg = msg
        self.status_color = color or THEME["green"]
        self.status_until = pygame.time.get_ticks() + int(secs * 1000)

    def toggle_hidapi(self):
        global HIDAPI_ENABLED
        new_val = not HIDAPI_ENABLED
        try:
            tmp = SETTINGS_FILE + ".tmp"
            with open(tmp, 'w') as f:
                json.dump({"hidapi": new_val}, f, indent=2)
            os.replace(tmp, SETTINGS_FILE)
            HIDAPI_ENABLED = new_val
            self.set_status(
                f"HIDAPI {'ON' if new_val else 'OFF'} - relaunch the tool to apply",
                THEME["accent"], 6.0,
            )
        except Exception as ex:
            self.set_status(f"Could not save settings: {ex}", THEME["warning"], 6.0)

    def load_json(self):
        if not os.path.exists(CONFIG_FILE):
            return {"input_config": []}
        if not os.path.exists(BACKUP_FILE):
            try:
                shutil.copyfile(CONFIG_FILE, BACKUP_FILE)
            except Exception as ex:
                self.set_status(f"Could not write backup: {ex}", THEME["warning"], 5.0)
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            if "input_config" not in data: data["input_config"] = []
            return data
        except Exception as ex:
            self.load_failed = True
            self.set_status(f"Config unreadable, saving disabled: {ex}", THEME["warning"], 8.0)
            return {"input_config": []}

    def save_json(self):
        if getattr(self, "load_failed", False):
            self.set_status("Save blocked: original config was unreadable (see Config.json.bak)", THEME["warning"], 6.0)
            return False
        has_keyboard = any(c.get("backend") == "WindowKeyboard" for c in self.config_data.get("input_config", []))
        if has_keyboard: self.config_data["enable_keyboard"] = True
        try:
            tmp = CONFIG_FILE + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            os.replace(tmp, CONFIG_FILE)
            self.set_status("Saved", THEME["green"], 2.0)
            return True
        except Exception as ex:
            self.set_status(f"SAVE FAILED: {ex}", THEME["warning"], 6.0)
            return False

    def convert_guid(self, guid):
        # Ryujinx stores the controller id as new Guid(sdlGuidHex).ToString(), where .NET's
        # Guid reverses the byte order of the first three fields (4-byte, 2-byte, 2-byte)
        # and leaves the rest as-is. Crucially, Ryujinx first ZEROES the CRC16 in bytes 2-3
        # (SDL stuffs a name/info checksum there that varies and shouldn't affect matching).
        # Verified against a Bluetooth Switch Pro Controller: SDL CRC 0x15b7 -> Ryujinx 0000.
        if len(guid) != 32: return guid
        b = [guid[i:i+2] for i in range(0, 32, 2)]  # 16 bytes
        b[2] = b[3] = "00"
        g1 = b[3] + b[2] + b[1] + b[0]
        g2 = b[5] + b[4]
        g3 = b[7] + b[6]
        g4 = b[8] + b[9]
        g5 = "".join(b[10:16])
        return f"{g1}-{g2}-{g3}-{g4}-{g5}"

    def get_guid_relative_index(self, target_joy):
        target_guid = target_joy.get_guid()
        count = 0
        for j in self.joysticks:
            if j.get_instance_id() == target_joy.get_instance_id(): return count
            if j.get_guid() == target_guid: count += 1
        return 0

    def setup_config_for_player(self):
        p_tag = f"Player{self.selected_slot+1}"
        existing = next((c for c in self.config_data["input_config"] if c.get("player_index") == p_tag), None)
        
        use_existing = False
        if existing:
            if self.active_device_type == "keyboard" and existing.get("backend") == "WindowKeyboard": use_existing = True
            elif self.active_device_type == "gamepad" and existing.get("backend") == "GamepadSDL2": use_existing = True
        
        if use_existing:
            conf = copy.deepcopy(existing)
        else:
            conf = copy.deepcopy(TEMPLATE_BASE)
            conf["player_index"] = p_tag
            if self.active_device_type == "keyboard":
                conf["backend"] = "WindowKeyboard"
                conf["id"] = "0"
                conf["name"] = "All keyboards"
                for k in ["left_joycon", "right_joycon"]: conf[k] = {x: "Unbound" for x in conf.get(k, {})}
                conf["left_joycon_stick"]["joystick"] = "Unbound"
                conf["right_joycon_stick"]["joystick"] = "Unbound"
                conf["left_joycon_stick"].update({"stick_up": "W", "stick_down": "S", "stick_left": "A", "stick_right": "D", "stick_button": "F"})
                conf["right_joycon_stick"].update({"stick_up": "I", "stick_down": "K", "stick_left": "J", "stick_right": "L", "stick_button": "H"})
                conf["left_joycon"].update({"dpad_up": "Up", "dpad_down": "Down", "dpad_left": "Left", "dpad_right": "Right"})

        if self.active_device_type == "gamepad":
            j = self.active_joy
            guid = self.convert_guid(j.get_guid())
            idx = self.get_guid_relative_index(j)
            conf["id"] = f"{idx}-{guid}"
            conf["name"] = f"{self.device_name(j)} ({idx})"
            self.current_target_list = TARGETS_GAMEPAD
        elif self.active_device_type == "keyboard":
            self.current_target_list = TARGETS_KEYBOARD

        return conf

    def update_config_value(self, conf, ryu_key, val):
        if "lstick_" in ryu_key: conf["left_joycon_stick"][f"stick_{ryu_key.split('_')[1]}"] = val
        elif "rstick_" in ryu_key: conf["right_joycon_stick"][f"stick_{ryu_key.split('_')[1]}"] = val
        elif ryu_key == "stick_button_left": conf["left_joycon_stick"]["stick_button"] = val
        elif ryu_key == "stick_button_right": conf["right_joycon_stick"]["stick_button"] = val
        elif ryu_key == "joystick_left": conf["left_joycon_stick"]["joystick"] = val
        elif ryu_key == "joystick_right": conf["right_joycon_stick"]["joystick"] = val
        elif ryu_key in ["button_a", "button_b", "button_x", "button_y", "button_plus", "button_r", "button_zr"]:
            conf["right_joycon"][ryu_key] = val
        elif ryu_key in ["button_minus", "button_l", "button_zl", "dpad_up", "dpad_down", "dpad_left", "dpad_right"]:
            conf["left_joycon"][ryu_key] = val

    def get_display_value(self, key):
        c = self.current_config
        if "lstick_" in key: return c["left_joycon_stick"].get(f"stick_{key.split('_')[1]}", "Unbound")
        if "rstick_" in key: return c["right_joycon_stick"].get(f"stick_{key.split('_')[1]}", "Unbound")
        if key == "stick_button_left": return c["left_joycon_stick"].get("stick_button", "Unbound")
        if key == "stick_button_right": return c["right_joycon_stick"].get("stick_button", "Unbound")
        if key == "joystick_left": return c["left_joycon_stick"].get("joystick", "Unbound")
        if key == "joystick_right": return c["right_joycon_stick"].get("joystick", "Unbound")
        val = c["left_joycon"].get(key)
        if val: return val
        val = c["right_joycon"].get(key)
        if val: return val
        return "Unbound"

    def translate_key(self, py_key):
        if py_key in KEY_TRANSLATION: return KEY_TRANSLATION[py_key]
        if len(py_key) == 1 and py_key.isalpha(): return py_key.upper()
        if len(py_key) == 1 and py_key.isdigit(): return f"Number{py_key}"
        if py_key.startswith("f") and py_key[1:].isdigit(): return py_key.upper()
        return py_key.title()






    def lerp(self, start_rect, end_rect, t):
        x = start_rect.x + (end_rect.x - start_rect.x) * t
        y = start_rect.y + (end_rect.y - start_rect.y) * t
        w = start_rect.width + (end_rect.width - start_rect.width) * t
        h = start_rect.height + (end_rect.height - start_rect.height) * t
        return pygame.Rect(x, y, w, h)

    def draw_shadow(self, rect, radius=12):
        shadow_surf = pygame.Surface((rect.width + 6, rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (*THEME["shadow"], 40), (0, 0, rect.width + 6, rect.height + 6), border_radius=radius)
        self.screen.blit(shadow_surf, (rect.x + 3, rect.y + 5))

    def draw_header(self, text, subtitle=""):
        h = self.s(100)
        pygame.draw.rect(self.screen, THEME["header_bg"], (0, 0, self.W, h))
        title = self.font_title.render(text, True, THEME["text"])
        self.screen.blit(title, (self.s(50), self.s(20)))
        if subtitle:
            sub = self.font_sm.render(subtitle, True, THEME["text_dim"])
            self.screen.blit(sub, (self.s(50), self.s(75)))
        pygame.draw.line(self.screen, THEME["divider"], (0, h), (self.W, h), 2)

    def draw_footer(self, left_text, right_text=""):
        fh = self.s(70)
        y = self.H - fh
        pygame.draw.rect(self.screen, THEME["header_bg"], (0, y, self.W, fh))
        pygame.draw.line(self.screen, THEME["divider"], (0, y), (self.W, y), 2)
        l_surf = self.font_sm.render(left_text, True, THEME["text_dim"])
        self.screen.blit(l_surf, (self.s(50), y + self.s(20)))
        if right_text:
            r_surf = self.font_sm.render(right_text, True, THEME["text_dim"])
            r_rect = r_surf.get_rect()
            r_rect.right = self.W - self.s(50)
            r_rect.top = y + self.s(20)
            self.screen.blit(r_surf, r_rect)

    # Icons not made by me, they were created by Gemini
    def draw_icon_check(self, x, y):
        pts = [(x, y+10), (x+10, y+20), (x+30, y)]
        pygame.draw.lines(self.screen, THEME["green"], False, pts, 4)

    def draw_icon_warn(self, x, y):
        pts = [(x+15, y), (x+30, y+25), (x, y+25)]
        pygame.draw.polygon(self.screen, THEME["warning"], pts)
        pygame.draw.line(self.screen, THEME["bg"], (x+15, y+8), (x+15, y+18), 2)
        pygame.draw.circle(self.screen, THEME["bg"], (x+15, y+22), 1)

    def draw_icon_controller(self, x, y):
        pygame.draw.rect(self.screen, THEME["text"], (x, y+5, 40, 25), border_radius=8)
        pygame.draw.circle(self.screen, THEME["bg"], (x+10, y+20), 4)
        pygame.draw.circle(self.screen, THEME["bg"], (x+30, y+20), 4)

    def draw_icon_keyboard(self, x, y):
        pygame.draw.rect(self.screen, THEME["text"], (x, y+5, 40, 25), border_radius=4)
        for i in range(3):
            pygame.draw.line(self.screen, THEME["bg"], (x+5, y+10+i*6), (x+35, y+10+i*6), 2)

    def draw_scroll_hint(self, direction, y):
        pulse = abs((self.animation_time % 1.0) - 0.5) * 2
        alpha = int(100 + pulse * 155)
        surf = pygame.Surface((30, 20), pygame.SRCALPHA)
        color = (*THEME["accent"], alpha)
        if direction == "up": pts = [(15, 0), (0, 20), (30, 20)]
        else: pts = [(0, 0), (30, 0), (15, 20)]
        pygame.draw.polygon(surf, color, pts)
        r = surf.get_rect(center=(self.W//2, y))
        self.screen.blit(surf, r)

    def register_cursor(self, rect):
        self.target_cursor_rect = rect
        if self.cursor_rect.width == 0: self.cursor_rect = rect

    def draw_animated_cursor(self, radius=12):
        self.cursor_rect = self.lerp(self.cursor_rect, self.target_cursor_rect, 0.25)
        self.draw_shadow(self.cursor_rect, radius)
        pygame.draw.rect(self.screen, THEME["panel_sel"], self.cursor_rect, border_radius=radius)
        pygame.draw.rect(self.screen, THEME["accent"], self.cursor_rect, 3, border_radius=radius)

    def draw_status_toast(self):
        if not self.status_msg or pygame.time.get_ticks() > self.status_until:
            return
        surf = self.font_md.render(self.status_msg, True, THEME["text"])
        pad = self.s(20)
        box = surf.get_rect()
        box.inflate_ip(pad * 2, pad)
        box.centerx = self.W // 2
        box.bottom = self.H - self.s(90)
        self.draw_shadow(box, 10)
        pygame.draw.rect(self.screen, THEME["panel_sel"], box, border_radius=10)
        pygame.draw.rect(self.screen, self.status_color, box, 3, border_radius=10)
        self.screen.blit(surf, surf.get_rect(center=box.center))

    def draw_diagnostics(self):
        # Shows exactly what SDL reports right now, so you can launch the tool through
        # Steam BPM vs. independently and compare. If the converted GUID / id differs
        # between the two, that's why Ryujinx (launched the other way) ignores a binding.
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((*THEME["bg"], 235))
        self.screen.blit(overlay, (0, 0))

        x, y = self.s(60), self.s(40)
        line_h = self.s(32)
        row_h = self.s(28)
        steam = os.environ.get("SteamAppId") or os.environ.get("SteamGameId")
        header = [
            "DIAGNOSTICS  (press [D] or [Back/View] to close)",
            f"Launched via Steam: {'YES (id ' + steam + ')' if steam else 'no'}    "
            f"Pads detected: {len(self.joysticks)}",
            f"SDL HIDAPI: {'ON' if HIDAPI_ENABLED else 'OFF'}    "
            f"[H] to toggle (then relaunch). Pick whichever matches your Ryujinx dropdown.",
            "Compare these values between your Steam-BPM launch and your independent launch.",
        ]
        for line in header:
            self.screen.blit(self.font_sm.render(line, True, THEME["accent"]), (x, y))
            y += line_h
        y += self.s(10)

        if not self.joysticks:
            self.screen.blit(self.font_md.render("No controllers connected.", True, THEME["text_dim"]), (x, y))
            return

        for i, j in enumerate(self.joysticks):
            raw = j.get_guid()
            ryu = self.convert_guid(raw)
            idx = self.get_guid_relative_index(j)
            is_ctrl = j.get_instance_id() in self.controller_ids
            name = self.device_name(j)
            lines = [
                (f"[{i}] {name}", THEME["text"]),
                (f"      HID name : {j.get_name()}", THEME["text_dim"]),
                (f"      raw GUID : {raw}", THEME["text_dim"]),
                (f"      Ryujinx  : id={idx}-{ryu}", THEME["text_dim"]),
                (f"      name     : {name} ({idx})", THEME["text_dim"]),
                (f"      input via: {'SDL controller (normalized)' if is_ctrl else 'raw button indices (fallback)'}",
                 THEME["green"] if is_ctrl else THEME["warning"]),
            ]
            for text, col in lines:
                self.screen.blit(self.font_sm.render(text, True, col), (x, y))
                y += row_h
            y += self.s(12)
            if y > self.H - self.s(60):
                break

    def render_menu(self):
        self.draw_header("Controller Configuration", "Configure up to 8 players")
        # Fit 4 rows of tiles between header and footer with even spacing.
        header_h = self.s(100)
        footer_h = self.s(70)
        margin = self.s(60)
        spacing = self.s(20)
        avail_h = self.H - header_h - footer_h - margin * 2
        item_h = max(self.s(60), (avail_h - spacing * 3) // 4)
        start_y = header_h + margin
        side_pad = self.s(60)
        col_gap = self.s(40)
        for i in range(MAX_PLAYERS):
            p_str = f"Player{i+1}"
            name = "Unconfigured"
            is_conf = False
            for c in self.config_data["input_config"]:
                if c.get("player_index") == p_str:
                    name = c.get("name", "Unknown")
                    is_conf = True

            col = i % 2
            row = i // 2
            w = (self.W - side_pad * 2 - col_gap) // 2
            x = side_pad + col * (w + col_gap)
            y = start_y + row * (item_h + spacing)

            rect = pygame.Rect(x, y, w, item_h)
            if i == self.selected_slot:
                self.register_cursor(rect)
                self.draw_animated_cursor(12)
            else:
                pygame.draw.rect(self.screen, THEME["panel"], rect, border_radius=12)

            cx = x + self.s(28)
            if is_conf: self.draw_icon_check(cx, y + item_h//2 - self.s(12))
            else: self.draw_icon_warn(cx, y + item_h//2 - self.s(12))
            cx += self.s(45)

            tc = THEME["text"] if i == self.selected_slot else THEME["text_dim"]
            self.screen.blit(self.font_md.render(f"Player {i+1}", True, tc), (cx, y + item_h//2 - self.s(15)))

            vc = THEME["accent"] if i == self.selected_slot else THEME["text_dim"]
            val_rect = self.font_sm.render(name, True, vc).get_rect(centery=y+item_h//2, right=x+w-self.s(28))
            self.screen.blit(self.font_sm.render(name, True, vc), val_rect)

        self.draw_footer("[ARROWS]/[DPAD]/[L Stick]: Navigate     [ENTER]/[A]: Configure", "[S]/[+]: Save All")

    def render_detect(self):
        self.draw_header(f"Player {self.selected_slot + 1} - Select Input")
        cx, cy = self.W // 2, self.H // 2
        card_rect = pygame.Rect(0, 0, self.s(750), self.s(340))
        card_rect.center = (cx, cy - self.s(30))

        pygame.draw.rect(self.screen, THEME["panel"], card_rect, border_radius=16)
        pygame.draw.rect(self.screen, THEME["divider"], card_rect, 2, border_radius=16)

        title = self.font_lg.render("Choose Input Method", True, THEME["text"])
        self.screen.blit(title, title.get_rect(center=(cx, card_rect.top + self.s(50))))

        self.draw_icon_controller(card_rect.left + self.s(80), card_rect.top + self.s(120))
        c_text = self.font_md.render("Press any button on Controller", True, THEME["text_dim"])
        self.screen.blit(c_text, (card_rect.left + self.s(140), card_rect.top + self.s(120)))

        ly = card_rect.top + self.s(170)
        pygame.draw.line(self.screen, THEME["divider"], (card_rect.left + self.s(60), ly), (card_rect.right - self.s(60), ly), 2)

        self.draw_icon_keyboard(card_rect.left + self.s(80), ly + self.s(50))
        k_text = self.font_md.render("Press [ENTER] for Keyboard", True, THEME["text_dim"])
        self.screen.blit(k_text, (card_rect.left + self.s(140), ly + self.s(50)))
        
        self.draw_footer("Waiting for input...", "[ESC]/[B]: Cancel")

    def render_mapping(self):
        dev_name = "Keyboard" if self.active_device_type == "keyboard" else self.device_name(self.active_joy)
        self.draw_header(f"Configure: {dev_name}", f"Player {self.selected_slot + 1}")
        targets = self.current_target_list
        header_h = self.s(100)
        footer_h = self.s(70)
        list_y = header_h + self.s(40)
        item_h = self.s(68)
        spacing = self.s(12)
        avail_h = self.H - list_y - footer_h - self.s(40)
        visible = max(3, min(9, avail_h // (item_h + spacing)))
        half = visible // 2
        start_idx = max(0, self.selected_map_index - half)
        if start_idx + visible > len(targets): start_idx = max(0, len(targets) - visible)

        side_pad = self.s(100)
        for i in range(visible):
            idx = start_idx + i
            if idx >= len(targets): break
            lbl, key = targets[idx]
            val = self.get_display_value(key)
            y = list_y + i * (item_h + spacing)
            w = self.W - side_pad * 2
            x = side_pad
            rect = pygame.Rect(x, y, w, item_h)

            if idx == self.selected_map_index:
                self.register_cursor(rect)
                self.draw_animated_cursor(10)
            else:
                pygame.draw.rect(self.screen, THEME["panel"], rect, border_radius=10)

            tc = THEME["text"] if idx == self.selected_map_index else THEME["text_dim"]
            self.screen.blit(self.font_md.render(lbl, True, tc), (x+self.s(24), y+item_h//2-self.s(15)))

            vc = THEME["accent"] if idx == self.selected_map_index else THEME["text_dim"]
            vr = self.font_sm.render(str(val), True, vc).get_rect(centery=y+item_h//2, right=x+w-self.s(24))
            pill = pygame.Rect(vr.left-self.s(12), vr.top-self.s(6), vr.width+self.s(24), vr.height+self.s(12))
            pc = THEME["bg"] if idx != self.selected_map_index else THEME["panel"]
            pygame.draw.rect(self.screen, pc, pill, border_radius=16)
            self.screen.blit(self.font_sm.render(str(val), True, vc), vr)

        if start_idx > 0: self.draw_scroll_hint("up", list_y - self.s(35))
        if start_idx + visible < len(targets): self.draw_scroll_hint("down", list_y + visible * (item_h + spacing) + self.s(20))
        
        hint = "[ENTER] Press Key" if self.active_device_type == "keyboard" else "[ENTER] Change Mapping"
        self.draw_footer(f"[ARROWS]/[DPAD]/[L Stick]: Navigate     {hint}", "[S]/[+]: Save & Return")

    def render_selector(self):
        self.render_mapping()
        if self.active_device_type == "keyboard":
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((*THEME["bg"], 220))
            self.screen.blit(overlay, (0,0))
            lbl, _ = self.current_target_list[self.selected_map_index]
            t1 = self.font_lg.render(f"Press Key for: {lbl}", True, THEME["accent"])
            self.screen.blit(t1, t1.get_rect(center=(self.W//2, self.H//2)))
            t2 = self.font_md.render("Press [ESC]/[B] to Cancel", True, THEME["text_dim"])
            self.screen.blit(t2, t2.get_rect(center=(self.W//2, self.H//2+self.s(50))))
            return

        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((*THEME["bg"], 200))
        self.screen.blit(overlay, (0,0))
        ih = self.s(58)
        title_h = self.s(90)
        hint_h = self.s(60)
        # Cap panel height to screen with margins so it fits on small displays.
        max_ph = self.H - self.s(80)
        vis = max(3, min(9, (max_ph - title_h - hint_h - self.s(20)) // ih))
        pw = self.s(600)
        ph = title_h + vis * ih + hint_h + self.s(20)
        px, py = (self.W - pw)//2, (self.H - ph)//2
        self.draw_shadow(pygame.Rect(px, py, pw, ph), radius=16)
        pygame.draw.rect(self.screen, THEME["bg"], (px, py, pw, ph), border_radius=16)
        pygame.draw.rect(self.screen, THEME["accent"], (px, py, pw, ph), 3, border_radius=16)
        pygame.draw.rect(self.screen, THEME["header_bg"], (px, py, pw, title_h), border_top_left_radius=16, border_top_right_radius=16)

        title = self.font_lg.render("Select Input", True, THEME["accent"])
        self.screen.blit(title, title.get_rect(center=(px+pw//2, py+title_h//2)))
        pygame.draw.line(self.screen, THEME["divider"], (px+self.s(20), py+title_h), (px+pw-self.s(20), py+title_h), 2)

        ly = py + title_h + self.s(20)
        if self.dropdown_index < self.dropdown_offset: self.dropdown_offset = self.dropdown_index
        elif self.dropdown_index >= self.dropdown_offset + vis: self.dropdown_offset = self.dropdown_index - vis + 1

        for i in range(vis):
            idx = self.dropdown_offset + i
            if idx >= len(DROPDOWN_MAP): break
            disp, _ = DROPDOWN_MAP[idx]
            dy = ly + i * ih
            rect = pygame.Rect(px+self.s(30), dy, pw-self.s(60), ih-self.s(6))
            is_sel = (idx == self.dropdown_index)
            col = THEME["panel_sel"] if is_sel else THEME["panel"]
            pygame.draw.rect(self.screen, col, rect, border_radius=8)
            if is_sel: pygame.draw.rect(self.screen, THEME["accent"], (px+self.s(30), dy, self.s(5), ih-self.s(6)), border_radius=8)
            tc = THEME["text"] if is_sel else THEME["text_dim"]
            self.screen.blit(self.font_md.render(disp, True, tc), (px+self.s(50), dy+self.s(12)))

        hint = self.font_sm.render("[ARROWS]/[DPAD]/[L Stick]: Navigate     [ENTER]/[A]: Select     [ESC]/[B]: Cancel", True, THEME["text_dim"])
        self.screen.blit(hint, hint.get_rect(center=(px+pw//2, py+ph-self.s(30))))






    def run(self):

        clock = pygame.time.Clock()
        while True:
            self.screen.fill(THEME["bg"])
            now = pygame.time.get_ticks() / 1000.0
            self.animation_time = now
            events = pygame.event.get()

            nav_dir = None
            select = False
            back = False
            save = False
            delete = False

            input_allowed = not self.input_locked()

            keys = pygame.key.get_pressed()
            joy_nav = None
            if len(self.joysticks) > 0:
                for j in self.joysticks:
                    if j.get_numhats() > 0:
                        hat = j.get_hat(0)
                        if hat[1]==1: joy_nav="up"
                        elif hat[1]==-1: joy_nav="down"
                        elif hat[0]==-1: joy_nav="left"
                        elif hat[0]==1: joy_nav="right"
                    if j.get_numaxes() >= 2:
                        if j.get_axis(1) < -0.5: joy_nav="up"
                        elif j.get_axis(1) > 0.5: joy_nav="down"
                        elif j.get_axis(0) < -0.5: joy_nav="left"
                        elif j.get_axis(0) > 0.5: joy_nav="right"
                    if joy_nav: break
            
            key_nav = None
            if keys[pygame.K_UP]: key_nav="up"
            elif keys[pygame.K_DOWN]: key_nav="down"
            elif keys[pygame.K_LEFT]: key_nav="left"
            elif keys[pygame.K_RIGHT]: key_nav="right"
            
            direction = joy_nav if joy_nav else key_nav
            if input_allowed and self.input_repeater.check(direction): nav_dir = direction

            for e in events:
                if e.type == pygame.QUIT: sys.exit()
                if e.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                    self.refresh_joysticks()
                if not input_allowed: continue
                
                if e.type == pygame.KEYDOWN:
                    if self.state == "SELECTOR" and self.active_device_type == "keyboard":
                         if e.key == pygame.K_ESCAPE: back = True
                         else: 
                             py_key = pygame.key.name(e.key)
                             ryu_key = self.translate_key(py_key)
                             target_key = self.current_target_list[self.selected_map_index][1]
                             self.update_config_value(self.current_config, target_key, ryu_key)
                             self.change_state("MAPPING")
                    else:
                        if e.key == pygame.K_RETURN: select = True
                        elif e.key == pygame.K_ESCAPE: back = True
                        elif e.key == pygame.K_s: save = True
                        elif e.key == pygame.K_r: delete = True
                        elif e.key == pygame.K_d: self.show_diag = not self.show_diag
                        elif e.key == pygame.K_h: self.toggle_hidapi()
                        if self.state == "DETECT" and e.key == pygame.K_RETURN:
                            self.active_device_type = "keyboard"
                            self.current_config = self.setup_config_for_player()
                            self.change_state("MAPPING")
                            select = False

                if e.type == pygame.CONTROLLERBUTTONDOWN:
                    if e.button == pygame.CONTROLLER_BUTTON_A: select = True       # bottom face = confirm
                    elif e.button == pygame.CONTROLLER_BUTTON_B: back = True       # right face = back
                    elif e.button == pygame.CONTROLLER_BUTTON_START: save = True
                    elif e.button == pygame.CONTROLLER_BUTTON_BACK: self.show_diag = not self.show_diag
                    if self.state == "DETECT":
                        self.pick_gamepad(e.instance_id)
                        select = False

                if e.type == pygame.JOYBUTTONDOWN and e.instance_id not in self.controller_ids:
                    if e.button == 0: select = True
                    if e.button == 1: back = True
                    if e.button == 7 or e.button == 6: save = True
                    if self.state == "DETECT":
                        self.pick_gamepad(e.instance_id)
                        select = False

            if self.state == "MENU":
                if nav_dir == "down": self.selected_slot = (self.selected_slot + 2) % MAX_PLAYERS
                elif nav_dir == "up": self.selected_slot = (self.selected_slot - 2) % MAX_PLAYERS
                elif nav_dir == "right": self.selected_slot = (self.selected_slot + 1) % MAX_PLAYERS
                elif nav_dir == "left": self.selected_slot = (self.selected_slot - 1) % MAX_PLAYERS
                if select: self.change_state("DETECT")
                if save:
                    if self.save_json(): sys.exit()

                if delete:
                    p_tag = f"Player{self.selected_slot+1}"
                    self.config_data["input_config"] = [c for c in self.config_data["input_config"] if c.get("player_index") != p_tag]
                    self.save_json()

                self.render_menu()

            elif self.state == "DETECT":
                self.render_detect()
                if back: self.change_state("MENU")

            elif self.state == "MAPPING":
                if nav_dir == "down": self.selected_map_index = (self.selected_map_index + 1) % len(self.current_target_list)
                elif nav_dir == "up": self.selected_map_index = (self.selected_map_index - 1) % len(self.current_target_list)
                if select:
                    self.change_state("SELECTOR")
                    self.dropdown_index = 0
                if back: self.change_state("MENU")
                if save:
                    self.config_data["input_config"] = [c for c in self.config_data["input_config"] if c.get("player_index") != self.current_config["player_index"]]
                    self.config_data["input_config"].append(self.current_config)
                    self.save_json()
                    self.change_state("MENU")
                self.render_mapping()

            elif self.state == "SELECTOR":
                if self.active_device_type == "keyboard": pass 
                else:
                    if nav_dir == "down": self.dropdown_index = (self.dropdown_index + 1) % len(DROPDOWN_MAP)
                    elif nav_dir == "up": self.dropdown_index = (self.dropdown_index - 1) % len(DROPDOWN_MAP)
                    if select:
                        _, internal_val = DROPDOWN_MAP[self.dropdown_index]
                        target_key = self.current_target_list[self.selected_map_index][1]
                        self.update_config_value(self.current_config, target_key, internal_val)
                        self.change_state("MAPPING")
                if back: self.change_state("MAPPING")
                self.render_selector()

            if self.show_diag: self.draw_diagnostics()
            self.draw_status_toast()
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    App().run()
