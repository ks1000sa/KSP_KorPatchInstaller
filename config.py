APP_NAME = "KSP 한글패치 통합설치기"
APP_VERSION = "3.0.0"
GITHUB_REPO = "ks1000sa/KSP_KorPatchFiles"
INSTALLER_REPO = "ks1000sa/KSP_KorPatchInstaller" 
PATCH_FILE_MAP = {
    "1.12.2 ~ 1.12.5 (latest)": 0,
    "1.12.0 ~ 1.12.1": 1,
    "1.11.1 ~ 1.11.2": 2,
    "1.11.0": 3,
    "1.10.0 ~ 1.10.1": 4,
}
PATCH_FILES = {
    0: {
        "K": ["0K1.cfg", "0K2.cfg"],
        "E": ["0E1.cfg", "0E2.cfg"]
    },
    1: {
        "K": ["1K1.cfg", "1K2.cfg"],
        "E": ["1E1.cfg", "1E2.cfg"]
    },
    2: {
        "K": ["2K1.cfg", "2K2.cfg"],
        "E": ["2E1.cfg", "2E2.cfg"]
    },
    3: {
        "K": ["3K1.cfg", "3K2.cfg"],
        "E": ["3E1.cfg", "3E2.cfg"]
    },
    4: {
        "K": ["4K1.cfg", "4K2.cfg"],
        "E": ["4E1.cfg", "4E2.cfg"]
    },
}
WELCOME_MESSAGE = f"""
KSP 한글패치 통합설치기 v{APP_VERSION}를 찾아주셔서 감사합니다.

많은 분들의 도움과 응원 덕분에 지금까지 한글패치 작업을 이어올 수 있었습니다.
앞으로도 더 나은 한글패치를 제공해드릴 수 있도록 노력하겠습니다.

설치를 시작하기 전, 실행 중인 모든 프로그램(특히 KSP)을 종료해 주세요.
정상적인 설치를 위해 실행 중인 KSP가 완전히 종료되어 있어야 합니다.

‘다음’ 버튼을 눌러 설치를 계속하시고,
‘종료’ 버튼을 눌러 설치를 종료할 수 있습니다.
"""
