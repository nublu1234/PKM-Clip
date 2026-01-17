# PKM-Clip

Personal Knowledge Management Tool - CLI 도구로 웹 콘텐츠를 로컬 마크다운 파일로 저장합니다.

## 개요

PKM-Clip은 웹 상의 다양한 글과 콘텐츠를 jina.ai reader를 활용하여 로컬 마크다운 파일로 자동 저장하는 CLI 도구입니다. 사용자는 웹페이지 URL만 입력하면 콘텐츠를 자동으로 추출하고, YAML frontmatter를 추가하여 구조화된 지식 베이스를 구축할 수 있습니다.

### 주요 기능

- **CLI 도구 우선 개발**: 커맨드 라인에서 간편하게 사용
- **Jina AI Reader 활용**: 웹페이지 → 마크다운 자동 변환
- **YAML Frontmatter**: 구조화된 메타데이터 자동 생성
- **Obsidian 호환**: Obsidian과 호환되는 마크다운 파일 생성
- **이미지 자동 처리**: 이미지 다운로드 및 로컬 참조 변환 (개발 예정)

## 설치

### 요구사항

- Python 3.9 이상

### 설치 방법

```bash
pip install -e .
```

## 설정

### 1. config.yaml 생성

`config.yaml.example`을 복사하여 설정 파일을 생성합니다:

```bash
cp config.yaml.example config.yaml
```

설정 파일 편집:

```yaml
image_path: ~/Attachments
default_tags:
  - clippings
jina_api:
  headers:
    x-with-generated-alt: false
    x-no-cache: false
    x-cache-tolerance: 3600
    x-respond-with: markdown
    x-timeout: 20
    Accept: "text/event-stream"
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 환경 변수 파일을 생성합니다:

```bash
cp .env.example .env
```

`.env` 파일에 Jina AI API 키를 입력합니다:

```bash
JINA_API_KEY=jn-xxxxxxxx
```

> **중요**: `.env` 파일은 `.gitignore`에 포함되어 있으므로 Git에 커밋되지 않습니다.

## 사용 방법

### 기본 사용법

```bash
pkm-clip clip <URL>
```

### 옵션

**Frontmatter 관련**

- `--tags TAGS`: 태그 추가 (쉼표로 구분)
- `--author AUTHOR`: 저자 직접 입력
- `--published DATE`: 게시일 직접 입력 (YYYY-MM-DD)
- `--description TEXT`: 설명 직접 입력

**출력 관련**

- `--output DIR`: 저장할 디렉토리 (기본값: 현재 디렉토리)
- `--filename NAME`: 파일명 직접 지정 (기본값: title 값)
- `--no-images`: 이미지 다운로드 스킵
- `--force`: 동일 파일명 존재 시 덮어쓰기

**설정 관련**

- `--config PATH`: config.yaml 파일 경로 지정
- `--verbose`: 상세 로그 출력
- `--dry-run`: 실제 저장 없이 결과만 확인

### 사용 예시

```bash
pkm-clip clip https://example.com/article
pkm-clip clip https://example.com/article --tags "clippings,learning"
pkm-clip clip https://example.com/article --output ~/Documents
pkm-clip --help
```

## 개발

### 개발 환경 설정

```bash
pip install -e ".[dev]"
```

### 테스트

```bash
pytest
```

### 코드 포맷팅 및 린팅

```bash
ruff format .
ruff check .
```

## 프로젝트 구조

```
PKM-Clip/
├── src/
│   ├── application/      # 유스케이스, CLI 명령
│   ├── domain/           # 비즈니스 로직, 엔티티
│   ├── infrastructure/    # 외부 API, 파일 시스템
│   ├── features/         # 기능별 모듈
│   └── main.py          # CLI 엔트리 포인트
├── tests/
│   ├── unit/
│   └── integration/
├── config.yaml.example
├── .env.example
└── pyproject.toml
```

## 라이선스

MIT

## 연락처

이슈가 있으면 GitHub Issues에 등록해주세요.
