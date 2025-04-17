import os, sys

def load_license(path="License.txt"):
    full_path = resource_path(path)
    if not os.path.exists(full_path):
        print(f"[ERROR] 텍스트 파일이 존재하지 않습니다: {full_path}")
        return ""
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    except UnicodeDecodeError as e:
        print(f"[ERROR] 인코딩 오류: {e}")
        return ""

    except PermissionError as e:
        print(f"[ERROR] 파일 권한 오류: {e}")
        return ""

    except OSError as e:
        print(f"[ERROR] 파일 열기 오류: {e}")
        return ""

    except Exception as e:
        print(f"[ERROR] 알 수 없는 오류 발생: {e}")
        return ""

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def save_log_file(logs):
    if isinstance(logs, list):
        logs = "\n".join(logs)

    filename = "KSP_KoreanPatcher_Log.txt"
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    save_path = os.path.join(desktop_path, filename)

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(logs)
        print(f"[INFO] 로그 저장 완료: {save_path}")
        return save_path
    except Exception as e:
        print(f"[ERROR] 로그 저장 실패: {e}")
        return None
