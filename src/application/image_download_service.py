"""
이미지 다운로드 서비스 모듈

마크다운 내 이미지 다운로드 및 Obsidian 참조 변환을 담당합니다.
"""

from typing import Dict

from src.domain.exceptions import ImageDownloadError
from src.domain.image_processor import ImageProcessor
from src.infrastructure.image_downloader import ImageDownloader
from src.infrastructure.logger import get_logger

logger = get_logger()


class ImageDownloadService:
    """
    이미지 다운로드 서비스

    마크다운 내 이미지 URL 추출, 다운로드, Obsidian 참조 변환을 수행합니다.
    """

    def __init__(
        self,
        image_processor: ImageProcessor | None = None,
        image_downloader: ImageDownloader | None = None,
    ) -> None:
        """
        이미지 다운로드 서비스 초기화

        Args:
            image_processor: 이미지 프로세서 (기본값: 새 인스턴스)
            image_downloader: 이미지 다운로더 (기본값: 새 인스턴스)
        """
        self.image_processor = image_processor or ImageProcessor()
        self.image_downloader = image_downloader or ImageDownloader()

    async def process_markdown_images(
        self,
        markdown: str,
        image_path: str,
        no_images: bool = False,
        dry_run: bool = False,
    ) -> tuple[str, int]:
        """
        마크다운 내 이미지를 처리합니다.

        Args:
            markdown: 마크다운 콘텐츠
            image_path: 이미지 저장 디렉토리
            no_images: 이미지 다운로드 스킵 여부
            dry_run: 실제 다운로드하지 않고 이미지 개수만 반환 (기본값: False)

        Returns:
            (이미지 처리된 마크다운 콘텐츠, 이미지 개수)
        """
        # --no-images 플래그가 설정된 경우 이미지 처리 스킵
        if no_images:
            logger.info("이미지 다운로드 스킵 (--no-images 플래그)")
            return markdown, 0

        # 이미지 URL 추출
        image_urls = self.image_processor.extract_image_urls(markdown)

        if not image_urls:
            logger.debug("마크다운 내 이미지 URL 없음")
            return markdown, 0

        logger.info(f"발견된 이미지 URL 개수: {len(image_urls)}")

        # dry-run 모드인 경우 이미지 다운로드 스킵
        if dry_run:
            logger.info("DRY-RUN 모드: 이미지 다운로드 스킵")
            return markdown, len(image_urls)

        # URL → 파일명 매핑
        url_to_filename: Dict[str, str] = {}

        # 각 이미지 다운로드
        for url in image_urls:
            logger.debug(f"이미지 처리 중: {url}")

            try:
                # 파일명 생성
                filename = self.image_processor.generate_filename(url)
                logger.debug(f"생성된 파일명: {filename}")

                # 이미지 다운로드 및 저장
                await self.image_downloader.download_and_save(
                    url=url,
                    image_path=image_path,
                    filename=filename,
                )

                # 매핑 저장
                url_to_filename[url] = filename
                logger.info(f"이미지 다운로드 완료: {url} -> {filename}")

            except ImageDownloadError as e:
                # 다운로드 실패 시 원본 URL 유지
                logger.warning(f"이미지 다운로드 실패, 원본 URL 유지: {url} - {e}")
                continue

        # Obsidian 참조로 변환
        if url_to_filename:
            logger.debug(f"Obsidian 참조 변환: {len(url_to_filename)}개 이미지")
            processed_markdown = self.image_processor.replace_with_obsidian_reference(
                markdown=markdown,
                url_to_filename=url_to_filename,
            )
            logger.info(f"이미지 처리 완료: {len(url_to_filename)}개 이미지 변환")
            return processed_markdown, len(url_to_filename)

        return markdown, 0
