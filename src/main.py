"""
PKM-Clip CLI 엔트리 포인트

Typer를 사용하여 CLI 명령어 인터페이스를 제공합니다.
"""

import asyncio

from typer import Typer

from src.application.models import FrontmatterOptions
from src.application.url_to_markdown_service import URLToMarkdownService
from src.infrastructure.config import AppConfig
from src.infrastructure.logger import get_logger, setup_logging

app = Typer(
    name="pkm-clip",
    help=(
        "PKM-Clip: Personal Knowledge Management Tool - "
        "웹페이지 콘텐츠를 로컬 마크다운 파일로 저장하는 CLI 도구"
    ),
    add_completion=False,
)


@app.command()
def clip(
    url: str,
    title: str | None = None,
    author: str | None = None,
    published: str | None = None,
    description: str | None = None,
    tags: str | None = None,
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
        title: 제목 직접 지정
        author: 저자 직접 입력
        published: 게시일 직접 입력 (YYYY-MM-DD)
        description: 설명 직접 입력
        tags: 추가할 태그 (쉼표로 구분)
        output: 저장할 디렉토리 (기본값: 현재 디렉토리)
        filename: 파일명 직접 지정 (기본값: title 값)
        no_images: 이미지 다운로드 스킵
        force: 동일 파일명 존재 시 덮어쓰기
        config: config.yaml 파일 경로
        verbose: 상세 로그 출력
        dry_run: 실제 저장 없이 결과만 확인
    """
    # 로깅 설정
    setup_logging(verbose=verbose)
    logger = get_logger()

    # CLI 옵션을 FrontmatterOptions로 변환
    cli_options = FrontmatterOptions(
        title=title,
        author=author,
        published=published,
        description=description,
        tags=tags.split(",") if tags else [],
    )

    # 설정 로드
    from src.infrastructure.config import Settings

    settings = Settings(config_path=config)

    # 서비스 초기화
    service = URLToMarkdownService(
        default_tags=settings.app.default_tags,
    )

    # 비동기로 URL 처리
    async def process() -> None:
        logger.info(f"URL 처리 시작: {url}")
        clipping = await service.process_url(url, options=cli_options)

        # 결과 출력
        logger.info(f"Clipping 생성 완료")
        logger.info(f"제목: {clipping.frontmatter.title}")
        logger.info(f"저자: {clipping.frontmatter.author}")
        logger.info(f"게시일: {clipping.frontmatter.published}")
        logger.info(f"태그: {clipping.frontmatter.tags}")

        if dry_run:
            logger.info("Dry-run 모드: 파일 저장하지 않음")
            print(f"---\n{clipping.to_markdown()}---")
        else:
            # 파일 저장 로직은 향후 Task에서 구현
            logger.info("파일 저장 기능은 향후 구현 예정")
            logger.info(f"생성된 마크다운:\n{clipping.to_markdown()}")

    asyncio.run(process())


@app.callback()
def main() -> None:
    """
    PKM-Clip - Personal Knowledge Management Tool
    """
    pass


if __name__ == "__main__":
    app()
