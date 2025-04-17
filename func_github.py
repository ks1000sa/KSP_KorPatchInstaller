import requests
import os, logging
from config import GITHUB_REPO, PATCH_FILE_MAP, PATCH_FILES

logger = logging.getLogger()

def load_theme():
    from func_file import resource_path
    try:
        path = resource_path("theme.cfg")
        with open(path, "rb") as f:
            raw = f.read()
        key = b't1kf2kdg0kqsl3ek'
        decoded = bytes([b ^ key[i % len(key)] for i, b in enumerate(raw)])
        return decoded.decode("utf-8")
    except Exception as e:
        logger.error(f"테마 로딩 실패: {e}")
        return None

def download_file_from_github(file_path, save_dir):
    logger.info(f"GitHub에서 파일 다운로드 요청: {file_path}")
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = get_custom_headers()
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        download_url = data["download_url"]
        logger.debug(f"다운로드 URL 확인: {download_url}")
        file_data = requests.get(download_url, headers=headers)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, os.path.basename(file_path))
        with open(save_path, 'wb') as f:
            f.write(file_data.content)
        logger.info(f"파일 다운로드 성공: {file_path} → {save_path}")
        return save_path
    else:
        logger.error(f"GitHub 파일 다운로드 실패: {file_path} (응답 코드: {res.status_code})")
        raise Exception(f"GitHub 파일 다운로드 실패: {file_path} ({res.status_code})")

def get_custom_headers():
    theme_value = load_theme()
    if theme_value:
        return {"Authorization": f"token {theme_value}"}
    else:
        logger.warning("테마 키 없음: GitHub 인증 실패")
        return {}
    
def get_file_last_commit_date(file_path):
    logger.info(f"커밋 날짜 요청: {file_path}")
    headers = get_custom_headers()
    if not headers:
        logger.warning("인증 헤더 없음: GitHub 연결 실패")
        return None

    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"
    params = {"path": file_path, "per_page": 1}
    res = requests.get(api_url, params=params, headers=headers)

    if res.status_code == 200:
        data = res.json()
        if data:
            full_date = data[0]["commit"]["committer"]["date"]
            logger.info(f"커밋 날짜 확인: {file_path} → {full_date}")
            return full_date[:10]
        else:
            logger.warning(f"커밋 없음: {file_path}")
    else:
        logger.error(f"API 실패 [{res.status_code}]: {file_path}")
    return None

def get_latest_release_version(repo_url):
    logger.info("최신 릴리즈 버전 확인 중...")
    api_url = f"https://api.github.com/repos/{repo_url}/releases/latest"
    headers = get_custom_headers()
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        latest = res.json().get("tag_name", "Unknown")
        logger.info(f"최신 릴리즈 버전: {latest}")
        return latest
    logger.error(f"최신 릴리즈 정보 조회 실패: {res.status_code}")
    return "Unknown"

def get_supported_mods():
    logger.info("지원 모드 목록 요청")
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/supported_mods"
    headers = get_custom_headers()
    if not headers:
        logger.warning("인증 헤더 없음: 모드 목록 불러오기 실패")
        return []

    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        mod_names = [item["name"] for item in data if item["type"] == "dir"]
        logger.info(f"모드 목록 불러오기 성공: {mod_names}")
        return mod_names
    else:
        logger.error(f"모드 목록 API 실패 [{res.status_code}]")
        return []

def update_patch_file_info(canvas, label_id, version_label, lang_key):
    logger.info(f"패치 파일 정보 업데이트: 버전={version_label}, 언어={lang_key}")
    patch_index = PATCH_FILE_MAP.get(version_label)
    if patch_index is None:
        canvas.itemconfig(label_id, text="❌ 패치 정보 없음")
        logger.warning("해당 버전에 대한 패치 정보 없음")
        return

    file_list = PATCH_FILES.get(patch_index, {}).get(lang_key, [])
    if not file_list:
        canvas.itemconfig(label_id, text="❌ 해당 언어의 파일 없음")
        logger.warning("해당 언어의 패치 파일 없음")
        return

    dates = []
    for fname in file_list:
        file_path = fname
        date = get_file_last_commit_date(file_path)
        if date:
            dates.append(date[:10])

    if dates:
        latest = max(dates)
        canvas.itemconfig(label_id, text=f"마지막 수정일: {latest}")
        logger.info(f"가장 최근 커밋 날짜: {latest}")
    else:
        canvas.itemconfig(label_id, text="❌ 수정일 불러오기 실패")
        logger.warning("커밋 날짜 불러오기 실패")
