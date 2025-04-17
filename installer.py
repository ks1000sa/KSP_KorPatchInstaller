import tkinter as tk
import logging, os, pygame, requests, shutil, sys, threading, webbrowser
from config import APP_NAME, APP_VERSION, PATCH_FILE_MAP, PATCH_FILES, WELCOME_MESSAGE, INSTALLER_REPO
from func_file import load_license, resource_path, save_log_file
from func_github import download_file_from_github, get_file_last_commit_date, get_latest_release_version, get_supported_mods #update_patch_file_info
from func_utils import in_memory_log_handler, animate_path, fade_image, find_user_path, is_mod_installed, reset_page, on_exit, on_volume_change, open_tutorial_video, play_music, select_manual_path, wrap_text
from packaging import version
from PIL import Image, ImageTk
from tkinter import Checkbutton, IntVar, messagebox, ttk

logger = logging.getLogger()

class LoadingPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("LoadingPage 로딩")
        self.master = master
        canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_01.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        self.image_widget = canvas.create_image(600, 300, anchor="center")
        self.image_refs = None
        self.loading_images = ["spacer.png", "Loading_01.png", "Loading_03.png", "Loading_02.png", "spacer.png"]
        self.current_index = 0
        self.canvas = canvas
        self.show_loading()
        self.canvas.bind("<Button-1>", self.skip)

    def show_loading(self):
        if self.current_index >= len(self.loading_images):
            if self.master.current_page == "LoadingPage":
                self.master.show_frame("WelcomePage")
            return
        
        self.default_steps = 20
        self.default_delay = 40
        self.spacer_steps = 1
        self.spacer_delay = 15
        current_img = self.loading_images[self.current_index]
        is_spacer = current_img.lower() == "spacer.png"
        fade_steps = self.spacer_steps if is_spacer else self.default_steps
        fade_delay = self.spacer_delay if is_spacer else self.default_delay

        def fade_in_callback():
            self.current_index += 1
            self.after(500, self.show_loading)

        if self.current_index > 0:
            prev_img = self.loading_images[self.current_index - 1]
            is_prev_spacer = prev_img.lower() == "spacer.png"
            prev_steps = self.spacer_steps if is_prev_spacer else self.default_steps
            prev_delay = self.spacer_delay if is_prev_spacer else self.default_delay

            fade_image(self.canvas, resource_path(prev_img), self.image_widget, fade_in=False, steps=prev_steps, delay=prev_delay, callback=lambda: 
                fade_image(self.canvas, resource_path(current_img), self.image_widget, fade_in=True, steps=fade_steps, delay=fade_delay, callback=fade_in_callback ))
        else:
            fade_image(self.canvas, resource_path(current_img), self.image_widget, fade_in=True, steps=fade_steps, delay=fade_delay, callback=fade_in_callback)

    def skip(self, event=None):
        self.master.show_frame("WelcomePage")

class WelcomePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("WelcomePage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_01.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        canvas.create_text(600, 60, text=WELCOME_MESSAGE, fill="white", font=("맑은 고딕", 20, "bold"), anchor="n", justify="center")
        canvas.create_text(550, 720, text="다음", fill="white", font=("맑은 고딕", 16, "bold"), activefill="skyblue", tags="next_btn")
        canvas.tag_bind("next_btn", "<Button-1>", lambda e: self.master.show_frame("LicensePage"))
        canvas.create_text(650, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas

class LicensePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("LicensePage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_02.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        canvas.create_text(770, 80, text="소프트웨어 사용권 안내", fill="white", font=("맑은 고딕", 25, "bold"), anchor="n", justify="center")
        text_frame = ttk.Frame(canvas, width=700, height=430)
        text_frame.pack_propagate(False)
        canvas.create_window(770, 430, window=text_frame, anchor="center")
        license_scroll = tk.Scrollbar(text_frame)
        license_scroll.pack(side="right", fill="y")
        text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=license_scroll.set, font=("맑은 고딕", 12), width=100, height=15, bg="black", fg="white", relief="flat", bd=0)
        text_widget.insert("1.0", load_license())
        text_widget.configure(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)
        license_scroll.config(command=text_widget.yview)

        self.agree_var = tk.BooleanVar(value=False)
        check_button = tk.Checkbutton(canvas, text="위 내용을 읽고 이해했습니다", variable=self.agree_var, command=self.update_next_state, font=("맑은 고딕", 12), bg="black", fg="white", activebackground="black", activeforeground="skyblue", selectcolor="black", relief="flat", highlightthickness=0, bd=0)
        canvas.create_window(1010, 670, window=check_button, anchor="center")
        canvas.create_text(1000, 720, text="다음", fill="gray", font=("맑은 고딕", 16, "bold"), tags="next_btn")
        canvas.tag_bind("next_btn", "<Enter>", self.on_next_hover)
        canvas.tag_bind("next_btn", "<Leave>", self.on_next_leave)
        canvas.tag_bind("next_btn", "<Button-1>", self.try_next)
        canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas    

    def on_next_hover(self, event):
        if self.agree_var.get():
            self.canvas.itemconfig("next_btn", fill="skyblue")

    def on_next_leave(self, event):
        if self.agree_var.get():
            self.canvas.itemconfig("next_btn", fill="white")
        else:
            self.canvas.itemconfig("next_btn", fill="gray")

    def try_next(self, event):
        if self.agree_var.get():
            self.master.show_frame("PlatformSettingsPage")

    def update_next_state(self):
        color = "white" if self.agree_var.get() else "gray"
        self.canvas.itemconfig("next_btn", fill=color)

class PlatformSettingsPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("PlatformSettingsPage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_03.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            logger.info("PlatformSettingsPage 배경 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"배경 이미지 로딩 실패: {e}")
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        canvas.create_text(770, 80, text="KSP 설치 플랫폼 선택", fill="white", font=("맑은 고딕", 25, "bold"), anchor="n", justify="center")
        self.platform_var = tk.StringVar(value="Steam")
        radio_frame = tk.Frame(canvas, bg="black")
        canvas.create_window(770, 250, window=radio_frame, anchor="center")
        steam_btn = tk.Radiobutton(radio_frame, text="Steam", value="Steam", variable=self.platform_var, font=("맑은 고딕", 14), bg="black", fg="white", selectcolor="black", activebackground="black", activeforeground="skyblue", highlightthickness=0)
        epic_btn = tk.Radiobutton(radio_frame, text="Epic Games", value="Epic", variable=self.platform_var, font=("맑은 고딕", 14), bg="black", fg="white", selectcolor="black", activebackground="black", activeforeground="skyblue", highlightthickness=0)
        manual_btn = tk.Radiobutton(radio_frame, text="경로 직접선택", value="Manual", variable=self.platform_var, font=("맑은 고딕", 14), bg="black", fg="white", selectcolor="black", activebackground="black", activeforeground="skyblue", highlightthickness=0)
        other_btn = tk.Radiobutton(radio_frame, text="경로 자동탐색 (시간이 다소 소요될 수 있음)", value="Other", variable=self.platform_var, font=("맑은 고딕", 14), bg="black", fg="white", selectcolor="black", activebackground="black", activeforeground="skyblue", highlightthickness=0)
        steam_btn.pack(anchor="w", pady=5)
        epic_btn.pack(anchor="w", pady=5)
        manual_btn.pack(anchor="w", pady=5)
        other_btn.pack(anchor="w", pady=5)
        self.logo_image = None
        self.logo_widget = canvas.create_image(770, 500, anchor="center")
        self.platform_var.trace_add("write", self.update_logo)

        canvas.create_text(900, 720, text="이전", fill="white", font=("맑은 고딕", 16, "bold"), activefill="light goldenrod", tags="prev_btn")
        canvas.tag_bind("prev_btn", "<Button-1>", lambda e: self.master.show_frame("LicensePage"))
        canvas.create_text(1000, 720, text="다음", fill="white", font=("맑은 고딕", 16, "bold"), activefill="skyblue", tags="next_btn")
        canvas.tag_bind("next_btn", "<Button-1>", lambda e: self.master.show_frame("PathSettingsPage"))
        canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas
        self.update_logo()
    
    def update_logo(self, *args):
        platform = self.platform_var.get()
        logger.info(f"플랫폼 선택됨: {platform}")
        image_map = {"Steam": "LOGO_01.png", "Epic": "LOGO_02.png", "Manual": "LOGO_03.png", "Other": "LOGO_04.png"}
        try:
            path = resource_path(image_map.get(platform, "IMG_PLATFORM_OTHER.png"))
            pil_img = Image.open(path).resize((215, 215))
            self.logo_image = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig(self.logo_widget, image=self.logo_image)
            logger.info("로고 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"로고 이미지 로딩 실패: {e}")
            
class PathSettingsPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("PathSettingsPage 로딩") 
        self.master = master
        self.searched = False
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_04.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            logger.info("PathSettingsPage 배경 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"배경 이미지 로딩 실패: {e}")
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        canvas.create_text(770, 80, text="KSP 설치 경로 탐색", fill="white", font=("맑은 고딕", 25, "bold"), anchor="n", justify="center")
        self.path_result_id = canvas.create_text(770, 180, text="", fill="white", font=("맑은 고딕", 12), anchor="center")
        canvas.create_text(770, 490, text=">> 한글패치 튜토리얼 영상 <<", fill="white", font=("맑은 고딕", 12), activefill="lightcoral", tags="guid_btn")
        canvas.tag_bind("guid_btn", "<Button-1>", lambda e: open_tutorial_video())
        canvas.create_text(600, 305, text="*설치 경로가 인식되지 않는 경우 '설치경로 직접선택'을 눌러\nKSP 실행파일(KSP_x64.exe)이 있는 폴더를 설치 경로로 설정해\n주시기 바랍니다. 설치 경로를 다시 인식시켜야 하는 경우\n'설치경로 재탐색'을 누르고 잠시 기다려 주시기 바랍니다.", fill="lightsalmon", font=("맑은 고딕", 10))
        canvas.create_text(1060, 280, text="설치경로 재탐색", fill="white", font=("맑은 고딕", 12), activefill="lime", tags="find_auto_btn")
        canvas.tag_bind("find_auto_btn", "<Button-1>", lambda e: self.update_path())
        canvas.create_text(1050, 330, text="설치경로 직접선택", fill="white", font=("맑은 고딕", 12), activefill="lime", tags="find_manual_btn")
        canvas.tag_bind("find_manual_btn", "<Button-1>", lambda e: self.open_manual_path_dialog())

        canvas.create_text(900, 720, text="이전", fill="white", font=("맑은 고딕", 16, "bold"), activefill="light goldenrod", tags="prev_btn")
        canvas.tag_bind("prev_btn", "<Button-1>", lambda e: self.master.show_frame("PlatformSettingsPage"))
        self.next_btn_id = canvas.create_text(1000, 720, text="다음", fill="white", font=("맑은 고딕", 16, "bold"), tags="next_btn")
        canvas.tag_bind("next_btn", "<Enter>", self.on_next_hover)
        canvas.tag_bind("next_btn", "<Leave>", self.on_next_leave)
        canvas.tag_bind("next_btn", "<Button-1>", self.on_next_clicked)
        canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas

    def open_manual_path_dialog(self):
        logger.info("설치경로 직접선택")
        selected = select_manual_path()
        if selected:
            logger.info(f"사용자 선택 경로: {selected}")
            self.update_path_from_manual(selected)
        else:
            logger.warning("선택한 경로에 KSP_x64.exe 없음")
            self.canvas.itemconfig(self.path_result_id, text="❌ 선택한 경로에 KSP_x64.exe가 존재하지 않습니다.")
            self.path_valid = False
            self.canvas.itemconfig(self.next_btn_id, fill="gray")

    def on_next_hover(self, event):
        if getattr(self, "path_valid", False):
            self.canvas.itemconfig(self.next_btn_id, fill="skyblue")

    def on_next_leave(self, event):
        if getattr(self, "path_valid", False):
            self.canvas.itemconfig(self.next_btn_id, fill="white")
        else:
            self.canvas.itemconfig(self.next_btn_id, fill="gray")

    def on_next_clicked(self, event):
        if hasattr(self, "path_valid") and self.path_valid:
            logger.info("유효한 설치경로")
            self.master.show_frame("InstallSettingsPage")
        else:
            logger.warning("실행파일이 누락된 경로")

    def update_path(self):
        logger.info("설치경로 자동 탐색 시작")
        self.canvas.itemconfig(self.path_result_id, text="경로를 탐색중입니다.")
        self.stop_dots = animate_path(self, text_prefix="경로를 탐색중입니다.", delay=400)

        def on_path_found(found_path):
            if hasattr(self, "stop_dots"):
                self.stop_dots()

            self.path_valid = False
            self.canvas.itemconfig(self.next_btn_id, fill="gray")

            if found_path:
                logger.info(f"자동 탐색 성공: {found_path}")
                wrapped = wrap_text(found_path, max_chars=90)
                self.canvas.itemconfig(self.path_result_id, text=wrapped)
                exe_path = os.path.join(found_path, "KSP_x64.exe")

                if os.path.exists(exe_path):
                    logger.info("KSP_x64.exe 확인")
                    self.path_valid = True
                    self.canvas.itemconfig(self.next_btn_id, fill="white")
                    self.master.install_path = found_path
                    self.master.frames["InstallSettingsPage"].load_mod_checkboxes()
                else:
                    logger.warning("KSP_x64.exe가 경로에 없음")
            else:
                logger.warning("자동 탐색 실패")
                self.canvas.itemconfig(self.path_result_id, text="❌ 설치 경로를 찾지 못했습니다.\n플랫폼 설정을 바꿔 경로탐색을 재시도하거나, 찾아보기를 눌러 경로를 직접 설정해 주세요.")

        platform = self.master.frames["PlatformSettingsPage"].platform_var.get()
        logger.info(f"선택된 플랫폼: {platform}")
        find_user_path(platform, lambda result: self.after(0, lambda: on_path_found(result)))

    def update_path_from_manual(self, path):
        logger.info(f"수동 설정 경로 적용: {path}")
        self.path_valid = True
        wrapped = wrap_text(path, max_chars=90)
        self.canvas.itemconfig(self.path_result_id, text=wrapped)
        self.canvas.itemconfig(self.next_btn_id, fill="white")
        self.master.install_path = path
        self.master.frames["InstallSettingsPage"].load_mod_checkboxes()

class InstallSettingsPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("InstallSettingsPage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_05.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            logger.info("InstallSettingsPage 배경 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"배경 이미지 로딩 실패: {e}")
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))
        
        self.mod_vars = {} 
        canvas.create_text(770, 80, text="KSP 설치 옵션", fill="white", font=("맑은 고딕", 25, "bold"), anchor="n", justify="center")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Transparent.TCombobox", fieldbackground="#1a1a1a", background="#1a1a1a", foreground="white", arrowcolor="white", borderwidth=0)
        version_label = tk.Label(self, text="사용중인 KSP 버전 :", bg="black", fg="white", font=("맑은 고딕", 12, "bold"))
        version_label.place(x=450, y=180)
        self.version_var = tk.StringVar(value="1.12.2 ~ 1.12.5 (latest)")
        version_combo = ttk.Combobox(self, values=["1.12.2 ~ 1.12.5 (latest)", "1.12.0 ~ 1.12.1", "1.11.1 ~ 1.11.2", "1.11.0", "1.10.0 ~ 1.10.1"], style="Transparent.TCombobox", textvariable=self.version_var)
        version_combo.place(x=850, y=186, width=250)
        #version_combo.bind("<<ComboboxSelected>>", lambda e: update_patch_file_info(self.canvas, self.date_label_id, self.version_var.get(), self.lang_var.get()))
        #self.date_label_id = canvas.create_text(940, 195, text="마지막 수정일 조회중...", fill="lightgray", font=("맑은 고딕", 10), anchor="w")
        lang_label = tk.Label(self, text="설치항목 :", bg="black", fg="white", font=("맑은 고딕", 12, "bold"))
        lang_label.place(x=450, y=220)
        self.lang_var = tk.StringVar(value="K")
        radio_ko = tk.Radiobutton(self, text="한글패치", value="K", variable=self.lang_var, bg="black", fg="white", activeforeground="skyblue", activebackground="black", selectcolor="black", font=("맑은 고딕", 12))
        #radio_ko.config(command=lambda: update_patch_file_info(self.canvas, self.date_label_id, self.version_var.get(), self.lang_var.get()))
        radio_en = tk.Radiobutton(self, text="영문패치", value="E", variable=self.lang_var, bg="black", fg="white", activeforeground="skyblue", activebackground="black", selectcolor="black", font=("맑은 고딕", 12))
        #radio_en.config(command=lambda: update_patch_file_info(self.canvas, self.date_label_id, self.version_var.get(), self.lang_var.get()))
        radio_ko.place(x=840, y=220)
        radio_en.place(x=1010, y=220)
        mod_label = tk.Label(self, text="모드 한글패치", bg="black", fg="white", font=("맑은 고딕", 12, "bold"))
        mod_label.place(x=450, y=260)

        canvas.create_text(900, 720, text="이전", fill="white", font=("맑은 고딕", 16, "bold"), activefill="light goldenrod", tags="prev_btn")
        canvas.tag_bind("prev_btn", "<Button-1>", lambda e: self.master.show_frame("PathSettingsPage"))
        canvas.create_text(1000, 720, text="다음", fill="white", font=("맑은 고딕", 16, "bold"), activefill="skyblue", tags="next_btn")
        canvas.tag_bind("next_btn", "<Button-1>", lambda e: self.master.show_frame("InstallPage"))
        canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas
        #update_patch_file_info(self.canvas, self.date_label_id, self.version_var.get(), self.lang_var.get())
        threading.Thread(target=self.load_mod_checkboxes, daemon=True).start()

    def load_mod_checkboxes(self):
        for widget in getattr(self, "checkbox_widgets", []):
            widget.destroy()
        self.checkbox_widgets = []

        mods = get_supported_mods()
        install_path = getattr(self.master, "install_path", None)
        logger.info(f"설치 경로에서 모드 확인: {install_path}")
        logger.info(f"감지된 모드 목록: {mods}")
        y = 300

        for mod in mods:
            var = IntVar()
            installed = is_mod_installed(install_path, mod)
            logger.info(f"{mod} 설치 여부: {'설치됨' if installed else '미설치'}")
            chk = Checkbutton(self, text=mod, variable=var, state="normal" if installed else "disabled", bg="black", fg="white", selectcolor="black", activebackground="black", activeforeground="skyblue", font=("맑은 고딕", 12))
            chk.place(x=500, y=y)
            self.mod_vars[mod] = var
            self.checkbox_widgets.append(chk)

            if installed:
                logger.debug(f"{mod} → ✔ 한글패치 가능")
                label = tk.Label(self, text="✔ 한글패치 가능", bg="black", fg="lightgreen", font=("맑은 고딕", 10))
            else:
                logger.debug(f"{mod} → ❌ 설치 안됨")
                label = tk.Label(self, text="❌ 모드가 설치가 감지되지 않아 한글패치 불가", bg="black", fg="gray", font=("맑은 고딕", 10))

            label.place(x=815, y=y+2)
            self.checkbox_widgets.append(label)

            y += 30
            
class InstallPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("InstallPage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_06.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            logger.info("InstallPage 배경 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"배경 이미지 로딩 실패: {e}")
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        self.progress = tk.IntVar(value=0)
        self.progress_label = tk.Label(self, text="설치를 시작하려면 '설치 시작'을 눌러주세요", bg="black", fg="white", font=("맑은 고딕", 12))
        self.progress_label.place(x=450, y=200)
        self.progress_bar = ttk.Progressbar(self, maximum=100, length=650, variable=self.progress)
        self.progress_bar.place(x=450, y=240)

        self.prev_btn_id = canvas.create_text(900, 720, text="이전", fill="white", font=("맑은 고딕", 16, "bold"), activefill="light goldenrod", tags="prev_btn")
        canvas.tag_bind("prev_btn", "<Button-1>", lambda e: self.master.show_frame("InstallSettingsPage"))
        self.start_btn_id = canvas.create_text(1000, 720, text="설치시작", fill="white", font=("맑은 고딕", 16, "bold"), activefill="skyblue", tags="next_btn")
        canvas.tag_bind("next_btn", "<Button-1>", lambda e: self.perform_installation())
        self.exit_id = canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas

    def cancel_installation(self):
        logger.info("설치 중단")
        self.master.show_frame("CancelPage")

    def reset(self):
        logger.info("설치 상태 초기화")
        self.progress.set(0)
        self.progress_label.config(text="설치를 시작하려면 '설치 시작'을 눌러주세요")

    def perform_installation(self):
        logger.info("설치 시작")
        self.reset()

        if hasattr(self, "start_btn_id"):
            self.canvas.delete(self.start_btn_id)
            self.canvas.delete(self.exit_id)
            self.canvas.delete(self.prev_btn_id)

        self.cancel_btn_id = self.canvas.create_text(1100, 720, text="설치취소", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="cancel_btn")
        self.canvas.tag_bind("cancel_btn", "<Button-1>", lambda e: self.cancel_installation())
        version = self.master.frames["InstallSettingsPage"].version_var.get()
        lang = self.master.frames["InstallSettingsPage"].lang_var.get()
        mod_vars = self.master.frames["InstallSettingsPage"].mod_vars
        install_path = self.master.install_path
        patch_index = PATCH_FILE_MAP.get(version)
        file_list = PATCH_FILES.get(patch_index, {}).get(lang, [])
        selected_mods = [mod for mod, var in mod_vars.items() if var.get() == 1]
        total_steps = len(file_list) + len(selected_mods)
        self.failures = []
        logger.info(f"설치 버전: {version}, 언어: {lang}")
        logger.info(f"패치 파일 수: {len(file_list)}, 선택된 모드 수: {len(selected_mods)}")
        logger.info(f"설치 경로: {install_path}")
        logger.debug(f"패치 파일 목록: {file_list}")
        logger.debug(f"선택된 모드 목록: {selected_mods}")
        temp_dir = os.path.join(install_path, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        logger.info(f"임시 폴더 생성됨: {temp_dir}")

        def step(index=0):
            if index < len(file_list):
                filename = file_list[index]
                logger.info(f"[{index+1}/{total_steps}] 파일 다운로드 시도: {filename}")

                try:
                    temp_path = download_file_from_github(filename, temp_dir)

                    if filename.endswith("K1.cfg"):
                        final_path = os.path.join(install_path, "GameData", "Squad", "Localization", "dictionary.cfg")
                    elif filename.endswith("K2.cfg"):
                        final_path = os.path.join(install_path, "GameData", "SquadExpansion", "Serenity", "Localization", "dictionary.cfg")
                    else:
                        final_path = None

                    if final_path:
                        os.makedirs(os.path.dirname(final_path), exist_ok=True)
                        shutil.copy(temp_path, final_path)
                        logger.info(f"파일 복사 완료: {filename} → {final_path}")

                    self.progress_label.config(text=f"{filename} 다운로드중...")
                    self.progress.set(int((index + 1) / total_steps * 100))
                except Exception as e:
                    logger.error(f"{filename} 설치 실패: {e}")
                    self.failures.append(f"{filename} - {str(e)}")
                    self.progress_label.config(text=f"❌ {filename} 실패: {e}")
            elif index < total_steps:
                mod_idx = index - len(file_list)
                modname = selected_mods[mod_idx]
                logger.info(f"[{index+1}/{total_steps}] 모드 설치 시도: {modname}")
                try:
                    mod_file_path = f"supported_mods/{modname}/Localization/en-us.cfg"
                    dest_dir = os.path.join(install_path, "GameData", modname, "Localization")
                    download_file_from_github(mod_file_path, dest_dir)
                    logger.info(f"{modname} 모드 한글패치 적용 완료")
                    self.progress_label.config(text=f"{modname} 모드 한글패치 다운로드중...")
                    self.progress.set(int((index + 1) / total_steps * 100))
                except Exception as e:
                    logger.error(f"{modname} 모드 설치 실패: {e}")
                    self.failures.append(f"{modname} - {str(e)}")
                    self.progress_label.config(text=f"❌ {modname} 실패: {e}")
            else:
                logger.info("모든 설치 항목 완료됨")
                self.progress_label.config(text="✔ 설치가 완료되었습니다! '다음'을 눌러 설치 과정을 마무리해 주세요")
                self.canvas.delete(self.cancel_btn_id)
                self.canvas.create_text(1100, 720, text="다음", fill="white", font=("맑은 고딕", 16, "bold"), activefill="skyblue", tags="next_btn")
                self.canvas.tag_bind("next_btn", "<Button-1>", lambda e: self.master.show_frame("CompletionPage"))

                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                        logger.info(f"temp 폴더 삭제 완료: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"temp 폴더 삭제 실패: {e}")

                if self.failures:
                    fail_msg = "\n".join(self.failures)
                    messagebox.showwarning("설치 일부 실패", f"다음 항목 설치에 실패했습니다:\n\n{fail_msg}")

                return

            self.after(1000, lambda: step(index + 1))

        step()
            
class CompletionPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("CompletionPage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_07.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            logger.info("CompletionPage 배경 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"CompletionPage 배경 이미지 로딩 실패: {e}")
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        canvas.create_text(770, 80, text="설치완료", fill="white", font=("맑은 고딕", 25, "bold"), anchor="n", justify="center")
        completion_message = '''
한글패치 설치가 완료되었습니다!

KSP 한글패치 통합설치기를 이용해 주셔서 진심으로 감사합니다.
사용 중 문제가 발생하거나 개선이 필요한 부분이 있다면,
언제든지 개발자 블로그 또는 디스코드 채널을 통해
소중한 의견을 남겨주시기 바랍니다.

앞으로도 지속적인 업데이트와 모드 한글화 지원을 통해
더 나은 게임 환경을 제공할 수 있도록 노력하겠습니다.

한글패치에 도움과 응원을 보내주신 모든 분들께
깊은 감사의 말씀을 드립니다. 감사합니다.
'''
        canvas.create_text(770, 330, text=completion_message, fill="white", font=("맑은 고딕", 14), justify="center", width=800)
        canvas.create_text(770, 530, text=">> 구버전 설치기 다운로드 <<", fill="white", font=("맑은 고딕", 12), tags="installer_btn", activefill="skyblue")
        canvas.tag_bind("installer_btn", "<Button-1>", lambda e: self.open_installer())
        canvas.create_text(770, 560, text=">> 개발자 블로그 바로가기 <<", fill="white", font=("맑은 고딕", 12), tags="blog_btn", activefill="skyblue")
        canvas.tag_bind("blog_btn", "<Button-1>", lambda e: self.open_blog())
        canvas.create_text(770, 590, text=">> 디스코드 서버 참여 <<", fill="white", font=("맑은 고딕", 12), tags="discord_btn", activefill="skyblue")
        canvas.tag_bind("discord_btn", "<Button-1>", lambda e: self.open_discord())
        canvas.create_text(770, 620, text=">> KSP 폴더 열기 <<", fill="white", font=("맑은 고딕", 12), tags="open_folder_btn", activefill="skyblue")
        canvas.tag_bind("open_folder_btn", "<Button-1>", lambda e: self.open_ksp_folder())

        canvas.create_oval(200, 390, 280, 600, outline="", fill="", tags="astronaut_easter_egg")
        canvas.tag_bind("astronaut_easter_egg", "<Button-1>", lambda e: self.show_quote())

        canvas.create_text(1000, 720, text="재설치", fill="white", font=("맑은 고딕", 16, "bold"), activefill="light goldenrod", tags="next_btn")
        canvas.tag_bind("next_btn", "<Button-1>", self.on_reset)
        canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas

    def show_quote(self):
        logger.info("이스터에그: 닐 암스트롱")
        messagebox.showinfo(
            "🌕 Neil Armstrong",
            '"That\'s one small step for a man,\n one giant leap for mankind."\n\n– Neil Armstrong'
        )

    def on_reset(self, event=None):
        reset_page(self.master, InstallPage)
        self.master.show_frame("PlatformSettingsPage")

    def open_blog(self):
        logger = logging.getLogger()
        logger.info("사용자가 개발자 블로그 열기 클릭")
        webbrowser.open("https://dobie.tistory.com/")

    def open_discord(self):
        logger = logging.getLogger()
        logger.info("사용자가 디스코드 서버 열기 클릭")
        webbrowser.open("https://discord.gg/ycZY67Vy2e")

    def open_installer(self):
        logger = logging.getLogger()
        logger.info("사용자가 구버전 설치기 클릭")
        webbrowser.open("https://dobie.tistory.com/118")

    def open_ksp_folder(self):
        logger = logging.getLogger()
        try:
            path = getattr(self.master, "install_path", None)
            if path and os.path.exists(path):
                os.startfile(path)
                logger.info(f"KSP 설치 경로 열기: {path}")
            else:
                logger.warning("설치 경로가 유효하지 않음.")
        except Exception as e:
            logger.error(f"KSP 폴더 열기 실패: {e}")
            
class CancelPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        logger.info("CancelPage 로딩")
        self.master = master
        canvas = tk.Canvas(self, width=1200, height=800, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_path = resource_path("IMG_08.png")
            pil_img = Image.open(bg_path).resize((1200, 800))
            self.bg_image = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            logger.info("CancelPage 배경 이미지 로딩 성공")
        except Exception as e:
            logger.error(f"CancelPage 배경 이미지 로딩 실패: {e}")
            canvas.create_text(100, 100, text="배경 이미지를 불러올 수 없음", fill="firebrick", font=("맑은 고딕", 20))

        canvas.create_text(770, 80, text="설치취소", fill="white", font=("맑은 고딕", 25, "bold"), anchor="n", justify="center")
        completion_message = '''
설치가 취소되었습니다.

설치 과정이 중단되어 KSP 한글패치가 정상적으로 적용되지 않았습니다.
'재설치'를 눌러 설치를 다시 시도하시거나, '로그파일 저장'을 통해
프로그램 사용 중 어떤 문제가 있었는지 확인해보실 수 있습니다.

궁금한 점이나 문제가 있으시다면 개발자 블로그 또는 디스코드 채널을 통해
언제든지 문의해 주세요.

만족스러운 경험을 드리지 못해 죄송합니다.
더욱 안정적인 한글패치를 제공할 수 있도록 최선을 다하겠습니다.

감사합니다.
'''
        canvas.create_text(770, 350, text=completion_message, fill="white", font=("맑은 고딕", 14), justify="center", width=800)
        canvas.create_text(770, 600, text=">> 로그파일 저장 <<", fill="white", font=("맑은 고딕", 12), tags="save_log_btn", activefill="skyblue")
        canvas.tag_bind("save_log_btn", "<Button-1>", self.on_save_log)
        canvas.create_text(770, 630, text=">> 구버전 설치기 다운로드 <<", fill="white", font=("맑은 고딕", 12), tags="installer_btn", activefill="skyblue")
        canvas.tag_bind("installer_btn", "<Button-1>", lambda e: self.open_installer())
        canvas.create_text(1000, 720, text="재설치", fill="white", font=("맑은 고딕", 16, "bold"), activefill="light goldenrod", tags="next_btn")
        canvas.tag_bind("next_btn", "<Button-1>", self.on_reset)
        canvas.create_text(1100, 720, text="종료", fill="white", font=("맑은 고딕", 16, "bold"), activefill="firebrick", tags="exit_btn")
        canvas.tag_bind("exit_btn", "<Button-1>", lambda e: on_exit(self))
        self.canvas = canvas

    def on_reset(self, event=None):
        reset_page(self.master, InstallPage)
        self.master.show_frame("PlatformSettingsPage")

    def open_installer(self):
        logger = logging.getLogger()
        logger.info("사용자가 구버전 설치기 클릭")
        webbrowser.open("https://dobie.tistory.com/118")
        
    def on_save_log(self, event=None):
        logger = logging.getLogger()
        logger.info("로그파일 저장요청")
        result = save_log_file(in_memory_log_handler.logs)
        if result:
            logger.info(f"로그파일 저장 완료: {result}")
            try:
                from tkinter import messagebox
                if messagebox.askyesno("로그 열기", "로그가 저장되었습니다.\n지금 열어보시겠습니까?"):
                    import os
                    if os.path.exists(result):
                        os.startfile(result)
            except Exception as e:
                logger.error(f"로그파일 열기 실패: {e}")
        else:
            logger.error("로그파일 저장 실패")

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        print("installerapp")
        self.title(f"{APP_NAME} v{APP_VERSION}")
        width, height = 1200, 800
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(width, height)
        self.resizable(False, False)
        self.iconbitmap(resource_path("icon.ico"))
        self.frames = {}
        threading.Thread(target=play_music, daemon=True).start()
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TScale", background="#ffffff", troughcolor="#333333", sliderlength=12, borderwidth=0, relief="flat")
        self.volume_var = tk.DoubleVar(value=25)
        self.volume_slider = ttk.Scale(
            self,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume_var,
            command=lambda val: (on_volume_change(val), self.update_speaker_icon())
        )
        self.volume_slider.place(x=1080, y=20, width=100)
        self.previous_volume = 0.25
        self.is_muted = False
        self.speaker_img = ImageTk.PhotoImage(Image.open(resource_path("icon_01.png")).resize((20, 20)))
        self.mute_img = ImageTk.PhotoImage(Image.open(resource_path("icon_02.png")).resize((20, 20)))
        self.speaker_btn = tk.Label(self, image=self.speaker_img, bg="#0c0e0d", cursor="hand2")
        self.speaker_btn.bind("<Button-1>", lambda e: self.toggle_mute())
        self.speaker_btn.place(x=1045, y=16, width=24, height=24)
        self.after(100, self.volume_slider.lift)
        self.after(100, self.speaker_btn.lift)

        for PageClass in (LoadingPage, WelcomePage, LicensePage, PlatformSettingsPage, PathSettingsPage, InstallSettingsPage, InstallPage, CompletionPage, CancelPage):
            page = PageClass(self)
            self.frames[PageClass.__name__] = page
            page.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("LoadingPage")
        self.check_github_connection()
        self.after(500, check_for_update)

    def toggle_mute(self):
        try:
            if self.is_muted:
                pygame.mixer.music.set_volume(self.previous_volume)
                self.volume_var.set(self.previous_volume * 100)
                self.speaker_btn.config(image=self.speaker_img)
                self.is_muted = False
            else:
                self.previous_volume = float(self.volume_var.get()) / 100
                pygame.mixer.music.set_volume(0)
                self.volume_var.set(0)
                self.speaker_btn.config(image=self.mute_img)
                self.is_muted = True
        except Exception as e:
            print("[ERROR] 음소거 토글 실패:", e)

    def check_github_connection(self):
        def worker():
            test_file = "0K1.cfg"
            date = get_file_last_commit_date(test_file)
            status = "🔗 GitHub 연결됨" if date else "❌ GitHub 연결 문제 발생, 시간이 지난 후(1시간 이상) 다시 시도해 주세요."
            self.after(0, lambda: self.update_connection_status(status))
        threading.Thread(target=worker, daemon=True).start()

    def update_connection_status(self, status):
        self.title(f"{APP_NAME} v{APP_VERSION}    -    {status}")

    def update_speaker_icon(self):
        volume = float(self.volume_var.get()) / 100
        if volume == 0:
            self.is_muted = True
            self.speaker_btn.config(image=self.mute_img)
        else:
            self.is_muted = False
            self.previous_volume = volume
            self.speaker_btn.config(image=self.speaker_img)

    def show_frame(self, page_name):
        previous_page = getattr(self, "current_page", None)
        frame = self.frames[page_name]
        frame.tkraise()
        self.current_page = page_name
        self.volume_slider.lift()
        self.speaker_btn.lift()

        if page_name == "PathSettingsPage" and previous_page == "PlatformSettingsPage":
            if hasattr(frame, "update_path"):
                self.after(100, frame.update_path)

def check_for_update():
    current = APP_VERSION
    latest = get_latest_release_version(INSTALLER_REPO)
    if latest != "Unknown" and version.parse(latest) > version.parse(current):
        if messagebox.askyesno("업데이트 확인", f"새 버전 v{latest}이(가) 있습니다.\n업데이트 하시겠습니까?"):
            download_and_run_update(latest, INSTALLER_REPO)

def download_and_run_update(tag, repo):
    url = f"https://github.com/{repo}/releases/download/{tag}/{tag}.exe"
    save_path = os.path.join(os.path.expanduser("~"), "Desktop", f"KSP 한글패치 설치기 v{tag}.exe")
    try:
        res = requests.get(url, stream=True)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(res.raw, f)
        messagebox.showinfo("업데이트 완료", f"{save_path} 에 저장됨\n곧 실행됩니다.")
        os.startfile(save_path)
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("업데이트 실패", f"오류 발생: {e}")

if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()