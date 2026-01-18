"""
마크다운 파일 결합기 모듈

YAML frontmatter와 마크다운 콘텐츠를 결합하여 하나의 마크다운 파일로 만듭니다.
"""

from typing import Any

import yaml

from src.infrastructure.logger import get_logger

logger = get_logger()


class MarkdownFileCombiner:
    """
    마크다운 파일 결합기 클래스

    YAML frontmatter와 마크다운 콘텐츠를 결합합니다.
    """

    def combine_frontmatter_and_markdown(
        self,
        frontmatter: dict[str, Any],
        markdown: str,
    ) -> str:
        """
        YAML frontmatter와 마크다운 콘텐츠를 결합합니다.

        Args:
            frontmatter: YAML frontmatter 딕셔너리
            markdown: 마크다운 콘텐츠 문자열

        Returns:
            결합된 마크다운 문자열 (frontmatter + content)

        Example:
            >>> combiner = MarkdownFileCombiner()
            >>> frontmatter = {"title": "Test", "tags": ["python"]}
            >>> markdown = "# Test\\n\\nContent here..."
            >>> result = combiner.combine_frontmatter_and_markdown(frontmatter, markdown)
            >>> print(result)
            ---
            title: Test
            tags:
            - python
            ---

            # Test

            Content here...
        """
        # 빈 frontmatter 처리
        if not frontmatter:
            logger.debug("빈 frontmatter, 마크다운만 반환")
            return markdown

        # 빈 markdown 처리
        if not markdown:
            markdown = ""

        # YAML frontmatter 문자열 생성
        yaml_frontmatter = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

        # 결합된 마크다운 생성
        combined = f"---\n{yaml_frontmatter}---\n\n{markdown}"

        # 끝에 불필요한 빈 줄 제거
        combined = combined.rstrip() + "\n"

        logger.debug(
            f"frontmatter와 markdown 결합 완료 "
            f"(frontmatter: {len(frontmatter)} 키, markdown: {len(markdown)} 자)"
        )

        return combined
