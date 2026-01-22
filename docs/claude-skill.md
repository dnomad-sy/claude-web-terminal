---
name: claude-web
description: Claude Web Terminal 서버를 시작하거나 종료합니다.
---

# Claude Web Terminal Skill

Claude Code에서 `/claude-web` 스킬로 사용하기 위한 설정 가이드입니다.

## 스킬 등록

`.claude/skills/claude-web/skill.md` 파일을 생성하고 아래 내용을 복사하세요:

```markdown
---
name: claude-web
description: Claude Web Terminal 서버를 시작하거나 종료합니다.
---

# Claude Web Terminal

웹 기반 Claude 터미널 서비스를 관리합니다.

## 사용법

/claude-web start [port]  # 서버 시작 (기본 포트: 6388)
/claude-web stop          # 서버 종료

## 워크플로우

### 인자 파싱

사용자 입력에서 명령과 포트를 추출:
- `start` 또는 인자 없음 → 서버 시작
- `start 8080` → 8080 포트로 서버 시작
- `stop` → 서버 종료

### start 명령 실행

cd "<claude-web-terminal 설치 경로>"
source .venv/bin/activate
python main.py start [port]

- 기본 포트: 6388
- PID 파일: ~/.claude-web.pid
- 서버 URL: http://localhost:[port]

### stop 명령 실행

cd "<claude-web-terminal 설치 경로>"
source .venv/bin/activate
python main.py stop

## 예시

### 서버 시작
사용자: /claude-web start
→ http://localhost:6388 에서 서버 시작

### 특정 포트로 시작
사용자: /claude-web start 8080
→ http://localhost:8080 에서 서버 시작

### 서버 종료
사용자: /claude-web stop
→ 실행 중인 서버 종료
```

## 환경 변수

스킬에서 경로를 동적으로 설정하려면 `$CLAUDE_WEB_DIR` 환경 변수를 사용하세요:

```bash
export CLAUDE_WEB_DIR="$HOME/path/to/claude-web-terminal"
```
