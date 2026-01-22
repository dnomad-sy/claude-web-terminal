---
name: claude-web
description: Claude Web Terminal 서버를 시작하거나 종료합니다.
---

# Claude Web Terminal

웹 기반 Claude 터미널 서비스를 관리합니다.

## 사용법

```
/claude-web start [port]  # 서버 시작 (기본 포트: 6388)
/claude-web stop          # 서버 종료
```

## 워크플로우

### 인자 파싱

사용자 입력에서 명령과 포트를 추출:
- `start` 또는 인자 없음 → 서버 시작
- `start 8080` → 8080 포트로 서버 시작
- `stop` → 서버 종료

### start 명령 실행

```bash
cd "$CLAUDE_PROJECT_DIR"
source .venv/bin/activate
python main.py start [port]
```

- 기본 포트: 6388
- PID 파일: ~/.claude-web.pid
- 서버 URL: http://localhost:[port]

### stop 명령 실행

```bash
cd "$CLAUDE_PROJECT_DIR"
source .venv/bin/activate
python main.py stop
```

## 의존성 설치 (최초 1회)

```bash
cd "$CLAUDE_PROJECT_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 예시

### 서버 시작
```
사용자: /claude-web start
→ http://localhost:6388 에서 서버 시작
```

### 특정 포트로 시작
```
사용자: /claude-web start 8080
→ http://localhost:8080 에서 서버 시작
```

### 서버 종료
```
사용자: /claude-web stop
→ 실행 중인 서버 종료
```
