"""
도메인 엔티티 모듈

비즈니스 로직의 핵심 엔티티를 정의합니다.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class MarkdownContent(BaseModel):
    """
    마크다운 콘텐츠 모델

    Jina AI Reader API를 통해 변환된 웹페이지 콘텐츠를 저장합니다.
    """

    url: str = Field(..., description="원본 URL")
    markdown: str = Field(..., description="변환된 마크다운 콘텐츠")
    fetched_at: datetime = Field(
        default_factory=datetime.now,
        description="콘텐츠를 가져온 시간 (UTC)",
    )

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """
        URL이 유효한 형식인지 확인합니다.

        Args:
            v: 검증할 URL

        Returns:
            유효한 URL

        Raises:
            ValueError: URL 형식이 올바르지 않은 경우
        """
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        return v.strip()


class Frontmatter(BaseModel):
    """
    마크다운 파일의 frontmatter 메타데이터

    문서의 메타데이터를 YAML 형식으로 저장합니다.
    """

    title: str = Field(..., description="문서 제목")
    source: str = Field(..., description="원본 URL")
    author: list[str] | None = Field(default=None, description="저자 정보 목록")
    published: date | None = Field(default=None, description="게시일 (YYYY-MM-DD)")
    created: date = Field(default_factory=date.today, description="클리핑 생성일")
    description: str | None = Field(default=None, description="문서 설명")
    tags: list[str] = Field(default_factory=list, description="태그 목록")

    @field_validator("created")
    @classmethod
    def validate_created(cls, v: date) -> date:
        """
        생성일이 항상 설정되도록 합니다.
        """
        if v is None:
            return date.today()
        return v


class Clipping(BaseModel):
    """
    클리핑 엔티티

    웹페이지에서 추출한 콘텐츠를 로컬 마크다운 파일로 저장하기 위한 데이터 구조입니다.
    """

    url: str = Field(..., description="원본 웹페이지 URL")
    frontmatter: Frontmatter = Field(..., description="YAML frontmatter 메타데이터")
    content: str = Field(default="", description="마크다운 콘텐츠")

    def to_markdown(self) -> str:
        """
        클리핑을 마크다운 형식으로 변환합니다.

        Returns:
            마크다운 문자열
        """
        import yaml

        fm_dict = self.frontmatter.model_dump(exclude_none=True, mode="json")
        fm_yaml = yaml.dump(fm_dict, allow_unicode=True, sort_keys=False)

        return f"---\n{fm_yaml}---\n\n{self.content}"
