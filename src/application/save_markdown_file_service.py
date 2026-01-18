"""
마크다운 파일 저장 서비스 모듈

URL에서 마크다운을 가져와 파일로 저장하는 전체 워크플로우를 조율합니다.
"""

from pathlib import Path
from typing import Final

from pydantic import BaseModel

from src.application.models import FrontmatterOptions
from src.application.url_to_markdown_service import URLToMarkdownService
from src.domain.filename_generator import FilenameGenerator
from src.domain.markdown_file_combiner import MarkdownFileCombiner
from src.infrastructure.logger import get_logger
from src.infrastructure.markdown_file_writer import MarkdownFileWriter

logger = get_logger()

# 기본 출력 디렉토리
DEFAULT_OUTPUT_DIR: Final = "~/Clippings"


class SaveMarkdownFileResult(BaseModel):
    """
    마크다운 파일 저장 결과
    """

    filepath: Path
    was_saved: bool
    content_size: int
    frontmatter: dict
    filename: str
    image_count: int = 0


class SaveMarkdownFileService:
    """
    마크다운 파일 저장 서비스

    URL에서 마크다운을 가져와 파일로 저장하는 전체 워크플로우를 조율합니다.
    """

    def __init__(
        self,
        url_to_markdown_service: URLToMarkdownService | None = None,
        filename_generator: FilenameGenerator | None = None,
        markdown_file_combiner: MarkdownFileCombiner | None = None,
        markdown_file_writer: MarkdownFileWriter | None = None,
    ) -> None:
        """
        서비스 초기화

        Args:
            url_to_markdown_service: URL to Markdown 서비스 (기본값: 새 인스턴스)
            filename_generator: 파일명 생성기 (기본값: 새 인스턴스)
            markdown_file_combiner: 마크다운 파일 결합기 (기본값: 새 인스턴스)
            markdown_file_writer: 마크다운 파일 작성기 (기본값: 새 인스턴스)
        """
        self.url_to_markdown_service = url_to_markdown_service or URLToMarkdownService()
        self.filename_generator = filename_generator or FilenameGenerator()
        self.markdown_file_combiner = markdown_file_combiner or MarkdownFileCombiner()
        self.markdown_file_writer = markdown_file_writer or MarkdownFileWriter()

    async def save_markdown_file(
        self,
        url: str,
        output_dir: str | None = None,
        filename: str | None = None,
        force: bool = False,
        frontmatter_options: FrontmatterOptions | None = None,
        image_path: str = "./Attachments",
        no_images: bool = False,
        dry_run: bool = False,
    ) -> SaveMarkdownFileResult:
        """
        URL에서 마크다운을 가져와 파일로 저장합니다.

        Args:
            url: 처리할 URL
            output_dir: 저장할 디렉토리 (기본값: ~/Clippings)
            filename: 파일명 직접 지정 (.md 제외)
            force: 파일이 존재할 때 덮어쓸지 여부
            frontmatter_options: Frontmatter 옵션
            image_path: 이미지 저장 경로
            no_images: 이미지 다운로드 스킵 여부
            dry_run: 실제 저장하지 않고 결과만 반환 (기본값: False)

        Returns:
            SaveMarkdownFileResult: 저장 결과 정보

        Raises:
            FileExistsError: 파일이 존재하고 force=False일 때
            DiskSpaceError: 디스크 공간이 부족할 때
            PermissionError: 쓰기 권한이 없을 때
        """
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = DEFAULT_OUTPUT_DIR
        output_path = Path(output_dir).expanduser()

        logger.info(f"파일 저장 시작: {url} -> {output_path}")

        # 1. URL에서 Clipping 생성
        clipping = await self.url_to_markdown_service.process_url(
            url=url,
            options=frontmatter_options,
            image_path=image_path,
            no_images=no_images,
            dry_run=dry_run,
        )

        # 2. 파일명 생성
        base_filename = self.filename_generator.generate_filename(
            title=clipping.frontmatter.title,
            custom_filename=filename,
        )

        # 3. 파일명 중복 처리 (force가 아닌 경우)
        final_filename = self._handle_duplicate_filename(
            output_path=output_path,
            base_filename=base_filename,
            force=force,
        )

        # 4. 파일 경로 생성
        filepath = output_path / f"{final_filename}.md"

        # 5. Frontmatter와 Markdown 결합
        frontmatter_dict = clipping.frontmatter.model_dump(mode="python")
        combined_markdown = self.markdown_file_combiner.combine_frontmatter_and_markdown(
            frontmatter=frontmatter_dict,
            markdown=clipping.content,
        )

        # 6. 파일 저장
        write_result = self.markdown_file_writer.write_markdown_file(
            content=combined_markdown,
            filepath=filepath,
            force=force,
            dry_run=dry_run,
        )

        logger.info(f"파일 저장 완료: {filepath}")

        # 7. 결과 반환
        image_count = getattr(clipping, "image_count", 0)
        return SaveMarkdownFileResult(
            filepath=write_result.filepath,
            was_saved=write_result.was_saved,
            content_size=write_result.content_size,
            frontmatter=frontmatter_dict,
            filename=final_filename,
            image_count=image_count,
        )

    def _handle_duplicate_filename(
        self,
        output_path: Path,
        base_filename: str,
        force: bool,
    ) -> str:
        """
        파일명 중복을 처리합니다.

        파일명이 이미 존재하는 경우 번호를 추가하여 새 파일명을 생성합니다.
        예: Title -> Title 1 -> Title 2 -> ...

        Args:
            output_path: 출력 디렉토리 경로
            base_filename: 기본 파일명
            force: 덮어쓰기 모드 여부

        Returns:
            중복이 처리된 파일명
        """
        # force 모드인 경우 기본 파일명 그대로 반환
        if force:
            return base_filename

        # 첫 번째 파일명 확인
        filepath = output_path / f"{base_filename}.md"

        if not filepath.exists():
            return base_filename

        # 중복 파일명 생성 (1부터 시작)
        counter = 1
        while True:
            numbered_filename = f"{base_filename} {counter}"
            filepath = output_path / f"{numbered_filename}.md"

            if not filepath.exists():
                logger.debug(f"중복 파일명 처리: {base_filename} -> {numbered_filename}")
                return numbered_filename

            counter += 1

            # 안전장치: 너무 많은 반복 방지
            if counter > 1000:
                logger.warning("파일명 중복 처리 반복 횟수 초과")
                break

        # 최후의 수단으로 타임스탬프 추가
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_filename}_{timestamp}"
