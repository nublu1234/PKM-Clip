"""
PKM-Clip CLI 엔트리 포인트

Typer를 사용하여 CLI 명령어 인터페이스를 제공합니다.
"""

import asyncio

from typer import Typer

from src.application.models import FrontmatterOptions
from src.application.save_markdown_file_service import SaveMarkdownFileService
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
    service = SaveMarkdownFileService()

    # 비동기로 URL 처리
    async def process() -> None:
        logger.info(f"URL 처리 시작: {url}")

        try:
            # 파일 저장
            result = await service.save_markdown_file(
                url=url,
                output_dir=output,
                filename=filename,
                force=force,
                frontmatter_options=cli_options,
                image_path=settings.app.image_path,
                no_images=no_images,
                dry_run=dry_run,
            )

            if dry_run:
                _display_dry_run_result(result)
            else:
                # 일반 모드 결과 출력
                logger.info(f"✅ 파일 저장 완료: {result.filepath}")
                print(f"✅ 파일 저장 완료: {result.filepath}")

        except Exception as e:
            logger.error(f"파일 저장 실패: {e}")
            print(f"❌ 파일 저장 실패: {e}")
            raise

    asyncio.run(process())


def _display_dry_run_result(result) -> None:
    """
    dry-run 모드 결과를 출력합니다.
    """
    print("\n" + "=" * 60)
    print("🔍 DRY-RUN MODE: 파일이 저장되지 않았습니다.")
    print("=" * 60)

    # 파일 경로 및 파일명
    print(f"\n📁 파일 경로: {result.filepath}")
    print(f"📄 파일명: {result.filename}")

    # Frontmatter 요약
    print("\n📋 Frontmatter:")
    frontmatter = result.frontmatter
    if "title" in frontmatter:
        print(f"   Title: {frontmatter.get('title')}")
    if "source" in frontmatter:
        print(f"   Source: {frontmatter.get('source')}")
    if "author" in frontmatter:
        print(f"   Author: {frontmatter.get('author')}")
    if "tags" in frontmatter:
        tags = frontmatter.get("tags", [])
        if tags:
            print(f"   Tags: {', '.join(tags)}")

    # 콘텐츠 정보
    print(f"\n📊 마크다운 콘텐츠 길이: {result.content_size:,} bytes")
    print(f"🖼️  발견된 이미지 개수: {result.image_count}")

    print("\n" + "=" * 60)
    print("💡 실제 저장을 하려면 --dry-run 옵션을 제거하세요.")
    print("=" * 60 + "\n")


@app.callback()
def main() -> None:
    """
    PKM-Clip - Personal Knowledge Management Tool
    """
    pass


if __name__ == "__main__":
    app()
