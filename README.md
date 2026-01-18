# PKM-Clip

Personal Knowledge Management Tool - CLI 도구로 웹 콘텐츠를 로컬 마크다운 파일로 저장합니다.

## 개요

PKM-Clip은 웹 상의 다양한 글과 콘텐츠를 jina.ai reader를 활용하여 로컬 마크다운 파일로 자동 저장하는 CLI 도구입니다. 사용자는 웹페이지 URL만 입력하면 콘텐츠를 자동으로 추출하고, YAML frontmatter를 추가하여 구조화된 지식 베이스를 구축할 수 있습니다.

### 주요 기능

- **CLI 도구 우선 개발**: 커맨드 라인에서 간편하게 사용
- **Jina AI Reader 활용**: 웹페이지 → 마크다운 자동 변환
- **YAML Frontmatter**: 구조화된 메타데이터 자동 생성
- **Obsidian 호환**: Obsidian과 호환되는 마크다운 파일 생성
- **이미지 자동 처리**: 이미지 다운로드 및 로컬 참조 변환

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
- `--no-images`: 이미지 다운로드 스킵 (기본값: false)
- `--force`: 동일 파일명 존재 시 덮어쓰기

**설정 관련**

- `--config PATH`: config.yaml 파일 경로 지정
- `--verbose`: 상세 로그 출력
- `--dry-run`: 실제 저장 없이 결과만 확인

### 사용 예시

```bash
# 기본 사용: 현재 디렉토리에 저장
pkm-clip clip https://example.com/article

# 특정 디렉토리에 저장
pkm-clip clip https://example.com/article --output ~/Documents

# 파일명 직접 지정
pkm-clip clip https://example.com/article --filename "my-article"

# 태그 추가
pkm-clip clip https://example.com/article --tags "clippings,learning"

# 동일 파일명 존재 시 덮어쓰기
pkm-clip clip https://example.com/article --force

# 이미지 다운로드 스킵
pkm-clip clip https://example.com/article --no-images

# 도움말 보기
pkm-clip --help
```

### 파일 저장

PKM-Clip은 자동으로 마크다운 파일을 저장합니다:

- **파일명**: 웹페이지 제목에서 자동 생성 (특수 문자는 `_`로 변환)
- **파일명 중복 처리**: `Title.md`, `Title 1.md`, `Title 2.md` 등 자동으로 번호 추가
- **덮어쓰기**: `--force` 옵션으로 기존 파일 덮어쓰기
- **디렉토리**: `--output` 옵션으로 저장 디렉토리 지정 (기본값: 현재 디렉토리)

#### 파일명 정규화

파일 시스템 호환성을 위해 다음 문자들이 `_`로 변환됩니다:

- `/ \ : * ? " < > |`

#### 예시 출력

```
✅ 파일 저장 완료: /home/user/Documents/Test Article.md
```

## 이미지 처리

PKM-Clip은 웹페이지 내 이미지를 자동으로 다운로드하고 Obsidian 호환 참조 형식으로 변환합니다.

### 이미지 처리 기능

- **자동 다운로드**: 웹페이지 내 모든 이미지를 `~/Attachments` 디렉토리에 다운로드
- **Obsidian 참조 변환**: `![alt](url)` 형식을 `![[filename]]` 형식으로 변환
- **중복 방지**: URL 기반 해시로 동일 이미지 중복 다운로드 방지
- **파일명 형식**: `YYYYMMDD_HHMMSS_{hash}.{extension}` (예: `20250116_145930_a3f2b1c4.png`)
- **에러 처리**: 다운로드 실패 시 원본 URL 유지 및 경고 로그 기록
- **파일 크기 제한**: 10MB 이하 이미지만 다운로드

### 이미지 설정

`config.yaml`에서 이미지 저장 경로를 설정할 수 있습니다:

```yaml
image_path: ~/Attachments # 이미지 저장 경로 (기본값: ~/Attachments)
```

### --no-images 옵션

이미지 다운로드를 건너뛰려면 `--no-images` 플래그를 사용하세요:

```bash
pkm-clip clip https://example.com/article --no-images
```

### Obsidian 참조 형식

변환 전:

```markdown
![alt text](https://example.com/image.png)
<img src="https://example.com/image.jpg" alt="alt text">
```

변환 후:

```markdown
![[20250116_145930_a3f2b1c4.png]]
![[20250116_145931_b4d2e5f6.jpg]]
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
