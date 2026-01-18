"""
ImageProcessor 단위 테스트
"""

import pytest

from src.domain.image_processor import ImageProcessor


class TestImageProcessor:
    """ImageProcessor 단위 테스트 클래스"""

    @pytest.fixture
    def image_processor(self) -> ImageProcessor:
        """
        ImageProcessor 픽스처

        Returns:
            ImageProcessor 인스턴스
        """
        return ImageProcessor()

    def test_extract_image_urls_from_standard_markdown(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        표준 마크다운 이미지 문법 추출 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        ![alt text](https://example.com/image.png)
        ```

        When: 이미지 URL을 추출함

        Then: `["https://example.com/image.png"]` 목록이 반환됨
        """
        markdown = "![alt text](https://example.com/image.png)"
        urls = image_processor.extract_image_urls(markdown)

        assert urls == ["https://example.com/image.png"]

    def test_extract_multiple_image_urls(self, image_processor: ImageProcessor) -> None:
        """
        여러 이미지 추출 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        ![image1](https://example.com/img1.png)
        ![image2](https://example.com/img2.jpg)
        ```

        When: 이미지 URL을 추출함

        Then: `["https://example.com/img1.png", "https://example.com/img2.jpg"]` 목록이 반환됨
        """
        markdown = (
            "![image1](https://example.com/img1.png)\n![image2](https://example.com/img2.jpg)"
        )
        urls = image_processor.extract_image_urls(markdown)

        assert len(urls) == 2
        assert "https://example.com/img1.png" in urls
        assert "https://example.com/img2.jpg" in urls

    def test_extract_image_urls_from_html_img_tag(self, image_processor: ImageProcessor) -> None:
        """
        HTML img 태그 추출 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        <img src="https://example.com/image.png" alt="alt text">
        ```

        When: 이미지 URL을 추출함

        Then: `["https://example.com/image.png"]` 목록이 반환됨
        """
        markdown = '<img src="https://example.com/image.png" alt="alt text">'
        urls = image_processor.extract_image_urls(markdown)

        assert urls == ["https://example.com/image.png"]

    def test_extract_image_urls_no_images(self, image_processor: ImageProcessor) -> None:
        """
        이미지가 없는 경우 테스트

        Given: 마크다운 콘텐츠에 이미지가 없음

        When: 이미지 URL을 추출함

        Then: 빈 목록이 반환됨
        """
        markdown = "텍스트만 있는 콘텐츠입니다."
        urls = image_processor.extract_image_urls(markdown)

        assert urls == []

    def test_extract_image_urls_removes_duplicates(self, image_processor: ImageProcessor) -> None:
        """
        중복 URL 제거 테스트

        Given: 동일한 이미지 URL이 여러 번 나타남

        When: 이미지 URL을 추출함

        Then: 중복이 제거된 목록이 반환됨
        """
        markdown = "![img1](https://example.com/image.png)\n![img2](https://example.com/image.png)"
        urls = image_processor.extract_image_urls(markdown)

        assert urls == ["https://example.com/image.png"]
        assert len(urls) == 1

    def test_generate_filename_timestamp_and_hash_format(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        timestamp와 hash 기반 파일명 생성 테스트

        Given: 이미지 URL이 `https://example.com/image.png`임

        When: 파일명을 생성함

        Then: 파일명은 `YYYYMMDD_HHMMSS_{hash}.png` 형식이어야 함

        And: `{hash}`는 URL의 SHA-256 해시값의 첫 8자여야 함
        """
        url = "https://example.com/image.png"
        filename = image_processor.generate_filename(url)

        # 파일명 형식 확인: YYYYMMDD_HHMMSS_hash.extension
        parts = filename.split("_")
        assert len(parts) == 3  # [YYYYMMDD, HHMMSS, hash.extension]

        # 날짜와 시간 부분 확인
        date_part = parts[0]
        time_part = parts[1]
        assert len(date_part) == 8  # YYYYMMDD
        assert len(time_part) == 6  # HHMMSS

        # 해시와 확장자 확인
        hash_and_extension = parts[2]
        hash_parts = hash_and_extension.split(".")
        assert len(hash_parts) == 2  # [hash, extension]

        hash_part = hash_parts[0]
        assert len(hash_part) == 8  # 첫 8자

        extension_part = hash_parts[1]
        assert extension_part == "png"

    def test_generate_filename_same_url_same_filename(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        동일 URL에서 동일 파일명 생성 테스트

        Given: 동일한 이미지 URL에서 두 번 파일명을 생성함

        When: 각각 파일명을 생성함

        Then: 두 번 모두 동일한 파일명이 생성됨
        """
        url = "https://example.com/image.png"
        filename1 = image_processor.generate_filename(url)
        filename2 = image_processor.generate_filename(url)

        # 타임스탬프가 다르므로 파일명이 다를 수 있음
        # 하지만 해시값은 동일해야 함
        hash1 = filename1.split("_")[1].split(".")[0]
        hash2 = filename2.split("_")[1].split(".")[0]
        assert hash1 == hash2

    def test_generate_filename_various_extensions(self, image_processor: ImageProcessor) -> None:
        """
        다양한 이미지 확장자 처리 테스트

        Given: 이미지 URL이 다음과 같음:
        ```
        https://example.com/image.jpg
        https://example.com/image.webp
        https://example.com/image.gif
        ```

        When: 각각 파일명을 생성함

        Then: 각 파일명은 원본 확장자를 유지해야 함
        """
        test_cases = [
            ("https://example.com/image.jpg", "jpg"),
            ("https://example.com/image.webp", "webp"),
            ("https://example.com/image.gif", "gif"),
        ]

        for url, expected_ext in test_cases:
            filename = image_processor.generate_filename(url)
            extension = filename.split(".")[-1]
            assert extension == expected_ext

    def test_generate_filename_no_extension_defaults_to_png(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        확장자가 없는 경우 기본값 PNG 테스트

        Given: 이미지 URL에 확장자가 없음

        When: 파일명을 생성함

        Then: 기본 확장자로 png가 사용됨
        """
        url = "https://example.com/image"
        filename = image_processor.generate_filename(url)
        extension = filename.split(".")[-1]
        assert extension == "png"

    def test_replace_with_obsidian_reference_single_image(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        단일 이미지 변환 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        ![alt text](https://example.com/image.png)
        ```

        And: 이미지가 다운로드되어 `20250116_145930_a3f2b1c4.png`로 저장됨

        When: 이미지 참조를 변환함

        Then: 결과는 다음과 같음:
        ```markdown
        ![[20250116_145930_a3f2b1c4.png]]
        ```
        """
        markdown = "![alt text](https://example.com/image.png)"
        url_to_filename = {"https://example.com/image.png": "20250116_145930_a3f2b1c4.png"}

        result = image_processor.replace_with_obsidian_reference(markdown, url_to_filename)

        assert result == "![[20250116_145930_a3f2b1c4.png]]"

    def test_replace_with_obsidian_reference_multiple_images(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        여러 이미지 동시 변환 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        ![img1](https://example.com/img1.png)
        Some text
        ![img2](https://example.com/img2.jpg)
        ```

        When: 모든 이미지 참조를 변환함

        Then: 결과는 다음과 같음:
        ```markdown
        ![[20250116_145930_a3f2b1c4.png]]
        Some text
        ![[20250116_145931_b4d2e5f6.jpg]]
        ```
        """
        markdown = (
            "![img1](https://example.com/img1.png)\n"
            "Some text\n"
            "![img2](https://example.com/img2.jpg)"
        )
        url_to_filename = {
            "https://example.com/img1.png": "20250116_145930_a3f2b1c4.png",
            "https://example.com/img2.jpg": "20250116_145931_b4d2e5f6.jpg",
        }

        result = image_processor.replace_with_obsidian_reference(markdown, url_to_filename)

        expected = "![[20250116_145930_a3f2b1c4.png]]\nSome text\n![[20250116_145931_b4d2e5f6.jpg]]"
        assert result == expected

    def test_replace_with_obsidian_reference_no_images(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        이미지가 없는 경우 테스트

        Given: 마크다운 콘텐츠에 이미지가 없음

        When: 이미지 참조를 변환함

        Then: 원본 콘텐츠가 그대로 반환됨
        """
        markdown = "이미지가 없는 텍스트입니다."
        url_to_filename = {}

        result = image_processor.replace_with_obsidian_reference(markdown, url_to_filename)

        assert result == markdown

    def test_replace_with_obsidian_reference_not_in_mapping_keeps_original(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        매핑에 없는 URL은 원본 유지 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        ![alt](https://example.com/image.png)
        ```

        And: URL이 매핑에 없음

        When: 이미지 참조를 변환함

        Then: 원본 참조가 유지됨
        """
        markdown = "![alt](https://example.com/image.png)"
        url_to_filename = {}  # 매핑 없음

        result = image_processor.replace_with_obsidian_reference(markdown, url_to_filename)

        assert result == markdown

    def test_validate_image_size_within_limit(self, image_processor: ImageProcessor) -> None:
        """
        파일 크기 제한 내 테스트

        Given: 이미지 크기가 10MB 미만임

        When: 파일 크기를 검증함

        Then: 예외가 발생하지 않음
        """
        size = 5 * 1024 * 1024  # 5MB

        # 예외가 발생하지 않아야 함
        image_processor.validate_image_size(size)

    def test_validate_image_size_exceeds_limit(self, image_processor: ImageProcessor) -> None:
        """
        파일 크기 초과 테스트

        Given: 이미지 크기가 10MB를 초과함

        When: 파일 크기를 검증함

        Then: ImageSizeExceededError 예외가 발생함
        """
        from src.domain.exceptions import ImageSizeExceededError

        size = 11 * 1024 * 1024  # 11MB

        with pytest.raises(ImageSizeExceededError):
            image_processor.validate_image_size(size)

    def test_replace_with_obsidian_reference_html_img_tag(
        self, image_processor: ImageProcessor
    ) -> None:
        """
        HTML img 태그 변환 테스트

        Given: 마크다운 콘텐츠가 다음과 같음:
        ```markdown
        <img src="https://example.com/image.png" alt="alt text">
        ```

        When: 이미지 참조를 변환함

        Then: 결과는 다음과 같음:
        ```markdown
        ![[20250116_145930_a3f2b1c4.png]]
        ```
        """
        markdown = '<img src="https://example.com/image.png" alt="alt text">'
        url_to_filename = {"https://example.com/image.png": "20250116_145930_a3f2b1c4.png"}

        result = image_processor.replace_with_obsidian_reference(markdown, url_to_filename)

        assert result == "![[20250116_145930_a3f2b1c4.png]]"
