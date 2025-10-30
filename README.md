# Class PDF Server

수업자료 PDF를 **업로드 → 즉시 브라우저에서 보기(다운로드 X)** 까지 제공하는 미니 서버 구성.

## 왜 배포(Deployment)가 필요한가?
- **재현성/안정성**: 로컬에서 만든 파일을 서버에 동일하게 반영(빌드/설정 포함) → 동작이 일관됨.
- **버전 관리/롤백**: Git으로 변경 이력 추적, 문제가 생기면 이전 버전으로 되돌리기 쉬움.
- **안전 분리**: 업로드 계정(uploader)은 SFTP로만 접근, 운영 설정(nginx, cloudflared, .htpasswd)은 코드와 분리.
- **자동화**: `deploy.sh`로 파일 동기화·서비스 재시작을 표준화(사람 손실 줄임).
- **포트폴리오 가치**: "설계→코드→배포→운영" 전체 사이클을 설명 가능.

## 기능
- **SFTP 업로드 전용계정**(chroot) → `/srv/class-pdf/pdfs`
- **Nginx(8080)**: `/pdfs/` 목록 & PDF inline 보기(`Content-Disposition: inline`)
- **Cloudflare Tunnel**: `https://pdf.jeonglab.site`로 공개 (HTTPS 자동)
- **Admin 전용**:
  - `/admin`: 드래그&드롭 업로드, 삭제 UI (Basic Auth 보호)
  - `/api`: 업로드/삭제 Flask API (127.0.0.1:9001, Nginx 프록시)
- **자동 인덱스**: `build_index.py`가 `/pdfs/` 스캔 → `site/index.json` 생성(5분마다 cron)

## 아키텍처
```
[Uploader (SFTP:2222)] --> [Nginx:8080] --> /srv/class-pdf/site (정적)
                                 |--> /pdfs (alias)
Admin(BasicAuth) --> /api ----> [Flask:127.0.0.1:9001]
Cloudflare Tunnel ----> https://pdf.jeonglab.site
```

## 디렉터리
- `/srv/class-pdf/pdfs` : 업로드 저장소(chroot, uploader 전용)
- `/srv/class-pdf/site` : 정적 사이트(index.html, admin.html, viewer.html, index.json)
- `/srv/class-pdf/build_index.py` : 목록 JSON 생성

## 보안/비공개(레포에 올리지 않음)
- `/etc/cloudflared/<UUID>.json`, `/etc/nginx/.htpasswd`

## 로컬 개발
정적 파일은 바로 브라우저에서 열람 가능(`site/index.html`, `site/admin.html`, `site/viewer.html`).  
운영에서 `/admin`은 Basic Auth, `/api`는 Nginx 프록시를 통해 접근.

## 빠른 배포 (요약)
1) GitHub에 새 레포 생성 → 이 디렉터리를 push
2) 서버 `/srv/class-pdf/app`로 clone
3) `deploy/deploy.sh` 실행 → 사이트/스크립트/Flask/Nginx 반영
4) (최초 1회) `crontab -e`로 `*/5 * * * * /srv/class-pdf/build_index.py` 등록

## SFTP 업로드 예시
```bash
sftp -P 2222 -i ~/.ssh/uploader_ed25519 uploader@<tailscale-ip>
cd pdfs
mkdir 2025-10-30 && cd 2025-10-30
put ./자료.pdf
```

## Admin API
- `POST /api/upload` (form-data: file=<pdf>, subdir=옵션)
- `POST /api/delete` (json: {"path":"/pdfs/2025-10-30/자료.pdf"})
- `GET  /api/health` (상태)

## 라이선스
MIT