# KSP Korean Patch Installer

This is a GUI-based installer for applying Korean translation patches to Kerbal Space Program (KSP).  
It automatically detects the game installation path, retrieves the latest patch files from GitHub, and applies them.

## Features

- Automatically detects KSP installation path (Steam, Epic, or custom)
- Applies translation patches to both the base game and supported mods
- Downloads the latest patch files directly from GitHub
- Installer built with Python and packaged using PyInstaller

## Build Instructions

To build the installer locally:

```bash
pip install -r requirements.txt
pyinstaller installer.py --onefile --windowed
```

> Note: Resource files (images, audio, configuration) are not included in this repository.

## Code Signing

This project uses [SignPath.io](https://signpath.io/open-source/) to digitally sign the installer executable.  
Signed builds are published to the [Releases](https://github.com/ks1000sa/KSP_KorPatchInstaller/releases) page.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Maintainer

Developed and maintained by Dobie.

-------------------------------------------------------------------------------------------------------------------

# KSP 한글패치 통합 설치기

이 프로젝트는 Kerbal Space Program(KSP)을 위한 GUI 기반 한글패치 설치기입니다.  
설치 경로를 자동으로 탐지하고, GitHub에서 최신 패치 파일을 다운로드하여 적용합니다.

## 주요 기능

- Steam, Epic Games, 수동 경로 자동 탐지
- 기본 게임 및 지원 모드에 번역 패치 적용
- GitHub에서 최신 패치 자동 다운로드
- Python + PyInstaller 기반 GUI 설치기

## 로컬 빌드 방법

다음 명령어로 설치기를 직접 빌드할 수 있습니다:

```bash
pip install -r requirements.txt
pyinstaller installer.py --onefile --windowed
```

> 참고: 이 저장소에는 이미지, 오디오, 설정 파일 등의 리소스가 포함되어 있지 않습니다.

## 코드 서명

이 프로젝트는 [SignPath.io](https://signpath.io/open-source/)를 사용하여 설치기 실행파일에 디지털 서명을 적용합니다.  
서명된 빌드는 [Releases](https://github.com/ks1000sa/KSP_KorPatchInstaller/releases) 탭에 게시됩니다.

## 라이선스

이 프로젝트는 MIT 라이선스로 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 개발자

개발 및 유지 관리: Dobie
