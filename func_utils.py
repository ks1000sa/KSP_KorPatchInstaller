import logging, os, pygame, shutil, string, threading, time, webbrowser
import tkinter.messagebox as msgbox
from func_file import resource_path
from PIL import Image, ImageTk
from tkinter import filedialog

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

class InMemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
in_memory_log_handler = InMemoryLogHandler()
in_memory_log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(in_memory_log_handler)
logger.setLevel(logging.DEBUG)

for name in ["urllib3", "requests", "PIL", "PIL.PngImagePlugin"]:
    l = logging.getLogger(name)
    l.setLevel(logging.DEBUG)
    l.addHandler(in_memory_log_handler)
    l.propagate = True

def animate_path(widget, text_prefix="처리중입니다", delay=500):
    state = {"dots": 0, "running": True}

    def loop():
        if not state["running"]:
            return
        dots = "." * (state["dots"] % 6)
        widget.canvas.itemconfig(widget.path_result_id, text=f"{text_prefix}{dots}")
        state["dots"] += 1
        widget.after(delay, loop)

    loop()

    def stop():
        state["running"] = False

    return stop

def fade_image(canvas, image_path, canvas_img_id, fade_in=True, steps=20, delay=40, callback=None):
    if not os.path.exists(image_path):
        logger.warning(f"fade 이미지 없음: {image_path}")
        if callback:
            callback()
        return {}

    try:
        pil_base = Image.open(image_path).convert("RGBA")
        original_data = pil_base.getdata()
    except Exception as e:
        logger.warning(f"fade 이미지 로딩 실패: {image_path} - {e}")
        if callback:
            callback()
        return {}
    
    alpha_start = 0 if fade_in else 255
    alpha_end = 255 if fade_in else 0
    image_refs = {}

    def step(i):
        if i > steps:
            if callback:
                callback()
            return

        alpha_factor = (alpha_start + (alpha_end - alpha_start) * i / steps) / 255
        faded_img = Image.new("RGBA", pil_base.size)
        faded_data = [(r, g, b, int(a * alpha_factor)) for (r, g, b, a) in original_data]
        faded_img.putdata(faded_data)
        tk_img = ImageTk.PhotoImage(faded_img)
        image_refs["img"] = tk_img
        canvas.itemconfig(canvas_img_id, image=tk_img)
        canvas.after(delay, lambda: step(i + 1))

    step(0)
    return image_refs

def find_custom_path(max_depth=7, timeout_seconds=25):
    print("🟡 사용자 지정 경로 탐색 중 (깊이 제한 + 타임아웃 포함)")
    start_time = time.time()
    valid_drives = [f"{d}:\\" for d in string.ascii_uppercase if d >= 'C' and os.path.exists(f"{d}:\\")]

    for drive in valid_drives:
        for root, dirs, files in os.walk(drive):

            if time.time() - start_time > timeout_seconds:
                print("⏱️ 타임아웃: 경로 탐색 중단")
                return None

            depth = root[len(drive):].count(os.sep)
            if depth > max_depth:
                dirs.clear()
                continue

            dirs[:] = [d for d in dirs if not d.startswith("$") and not d.lower().startswith("system")]

            if "kerbal space program" in root.lower().replace("/", "\\"):
                for fname in ["KSP_x64.exe", "ksp_x64.exe"]:
                    exe_path = os.path.join(root, fname)
                    if os.path.exists(exe_path):
                        print(f"✅ 경로 탐색 성공: {exe_path}")
                        return root

    print("❌ 타임아웃 되었거나, 설치 경로를 찾지 못했습니다.")
    return None

def find_epic_path():
    print("⚫ Epic Games 설치 경로 자동 감지 실행")
    valid_drives = [f"{d}:\\" for d in string.ascii_uppercase if d >= 'C' and os.path.exists(f"{d}:\\")]
    common_subpaths = [
        os.path.join("Epic Games", "KerbalSpaceProgram", "KSP_x64.exe"),
        os.path.join("Games", "KerbalSpaceProgram", "KSP_x64.exe"),
    ]

    for drive in valid_drives:
        for subpath in common_subpaths:
            full_path = os.path.join(drive, subpath)
            if os.path.exists(full_path):
                return os.path.dirname(full_path)

    return None

def find_manual_path():
    print("🟤 사용자 직접 경로 설정 모드")
    return "'설치경로 재탐색'을 선택해 경로를 직접 설정해 주세요"

def find_steam_path():
    print("🔵 Steam 설치 경로 자동 감지 실행")
    valid_drives = [f"{d}:\\" for d in string.ascii_uppercase if d >= 'C' and os.path.exists(f"{d}:\\")]
    common_subpaths = [
        os.path.join("SteamLibrary", "steamapps", "common", "Kerbal Space Program", "KSP_x64.exe"),
        os.path.join("Program Files (x86)", "Steam", "steamapps", "common", "Kerbal Space Program", "KSP_x64.exe"),
        os.path.join("Steam", "steamapps", "common", "Kerbal Space Program", "KSP_x64.exe")
    ]

    for drive in valid_drives:
        for subpath in common_subpaths:
            full_path = os.path.join(drive, subpath)
            if os.path.exists(full_path):
                return os.path.dirname(full_path)

    return None

def find_user_path(platform, callback):
    def worker():
        try:
            if platform == "Steam":
                result = find_steam_path()
            elif platform == "Epic":
                result = find_epic_path()
            elif platform == "Manual":
                result = find_manual_path()
            else:
                result = find_custom_path()
        except Exception as e:
            print(f"[ERROR] 경로 탐색 실패: {e}")
            result = None
        callback(result)

    threading.Thread(target=worker, daemon=True).start()

def is_mod_installed(install_path, mod_name):
    if not install_path:
        return False

    if mod_name.lower() in ["squad", "squadexpansion"]:
        return False

    mod_path = os.path.join(install_path, "GameData", mod_name)
    return os.path.exists(mod_path)

def on_exit(self, event=None):
    if msgbox.askyesno("종료 확인", "정말로 한글패치 통합설치기를 종료하시겠습니까?"):
        pygame.mixer.music.stop()
        self.master.destroy()

def reset_page(app, page_class):
    page_name = page_class.__name__
    install_path = getattr(app, "install_path", None)
    if install_path:
        temp_path = os.path.join(install_path, "temp")
        if os.path.exists(temp_path):
            try:
                shutil.rmtree(temp_path)
                print(f"[INFO] 기존 temp 폴더 삭제 완료: {temp_path}")
            except Exception as e:
                print(f"[ERROR] temp 폴더 삭제 실패: {e}")

    if page_name in app.frames:
        app.frames[page_name].destroy()
        del app.frames[page_name]

    new_page = page_class(app)
    app.frames[page_name] = new_page
    new_page.place(x=0, y=0, relwidth=1, relheight=1)

def on_volume_change(value):
    try:
        volume = float(value) / 100
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(volume)
    except Exception as e:
        print(f"[ERROR] 볼륨 조절 실패: {e}")

def open_tutorial_video():
    webbrowser.open("https://www.youtube.com/watch?v=9JH7XRLuQrA")

def play_music():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path("BGM.mp3"))
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("[ERROR] 음악 재생 실패:", e)
        
def select_manual_path():
    selected_dir = filedialog.askdirectory(title="KSP 설치 폴더를 선택하세요")

    if not selected_dir:
        return None

    exe_path = os.path.join(selected_dir, "KSP_x64.exe")
    if os.path.exists(exe_path):
        return selected_dir
    else:
        return None

def wrap_text(text, max_chars=90):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += (word + " ")
        else:
            lines.append(current_line.rstrip())
            current_line = word + " "

    lines.append(current_line.rstrip())
    return "\n".join(lines)
