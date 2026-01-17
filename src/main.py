"""
PKM-Clip CLI 엔트리 포인트

Typer를 사용하여 CLI 명령어 인터페이스를 제공합니다.
"""

from typer import Typer

app = Typer(
    name="pkm-clip",
    help="PKM-Clip: Personal Knowledge Management Tool - 웹 콘텐츠를 로컬 마크다운 파일로 저장하는 CLI 도구",
    add_completion=False,
)


@app.command()
def clip(
    url: str,
    tags: str | None = None,
    author: str | None = None,
    published: str | None = None,
    description: str | None = None,
    output: str = ".",
    filename: str | None = None,
    no_images: bool = False,
    force: bool = False,
    config: str = "config.yaml",
    verbose: bool = False,
    dry_run: bool = False,
) -> None:
    """
    웹페이지 콘텐츠를 로컬 마크다운 파일로 저장합니다.

    Args:
        url: 저장할 웹페이지 URL
        tags: 추가할 태그 (쉼표로 구분)
        author: 저자 직접 입력
        published: 게시일 직접 입력 (YYYY-MM-DD)
        description: 설명 직접 입력
        output: 저장할 디렉토리 (기본값: 현재 디렉토리)
        filename: 파일명 직접 지정 (기본값: title 값)
        no_images: 이미지 다운로드 스킵
        force: 동일 파일명 존재 시 덮어쓰기
        config: config.yaml 파일 경로
        verbose: 상세 로그 출력
        dry_run: 실제 저장 없이 결과만 확인
    """
    from src.infrastructure.config import Settings
    from src.infrastructure.logger import setup_logging, get_logger

    setup_logging(verbose=verbose)
    logger = get_logger()

    logger.info(f"PKM-Clip URL processing started: {url}")
    logger.info("기능 구현 예정 - 프로젝트 구조 설정 완료")


@app.callback()
def main() -> None:
    """
    PKM-Clip - Personal Knowledge Management Tool
    """
    pass


if __name__ == "__main__":
    app()
