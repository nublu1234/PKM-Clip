from __future__ import annotations

"""
설정 로드 모듈

Pydantic을 사용하여 config.yaml과 .env 파일에서 설정을 로드하고 검증합니다.
"""

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """
    애플리케이션 기본 설정

    비민감 설정을 포함합니다.
    """

    image_path: str = Field(
        default="~/Attachments",
        description="이미지 저장 경로",
    )
    default_tags: list[str] = Field(
        default_factory=lambda: ["clippings"],
        description="기본 태그 목록",
    )

    @field_validator("image_path")
    @classmethod
    def expand_home_path(cls, v: str) -> str:
        """
        ~ 표시를 사용자 홈 디렉토리로 확장합니다.
        """
        return str(Path(v).expanduser())


class JinaAPIConfig(BaseSettings):
    """
    Jina AI Reader API 설정

    민감 설정을 포함하며 환경 변수에서 로드합니다.
    """

    model_config = SettingsConfigDict(env_prefix="JINA_", env_file=".env")

    api_key: str = Field(..., description="Jina AI API 키")
    base_url: str = Field(default="https://r.jina.ai", description="Jina Reader API 기본 URL")
    headers: dict[str, Any] = Field(
        default={
            "x-with-generated-alt": False,
            "x-no-cache": False,
            "x-cache-tolerance": 3600,
            "x-respond-with": "markdown",
            "x-timeout": 20,
            "Accept": "text/event-stream",
        },
        description="API 요청 헤더",
    )
    timeout: int = Field(default=20, description="요청 타임아웃 (초)")
    max_retries: int = Field(default=3, description="최대 재시도 횟수")
    retry_delay: int = Field(default=1, description="초기 재시도 대기 시간 (초)")
    retry_multiplier: float = Field(default=2.0, description="지수 백오프 배수")


class Settings:
    """
    전체 애플리케이션 설정

    AppConfig와 JinaAPIConfig를 포함합니다.
    """

    def __init__(self, config_path: str = "config.yaml") -> None:
        """
        설정을 로드합니다.

        Args:
            config_path: config.yaml 파일 경로
        """
        load_dotenv()

        self.app = self._load_app_config(config_path)
        self.jina_api = JinaAPIConfig()

    def _load_app_config(self, config_path: str) -> AppConfig:
        """
        YAML 파일에서 앱 설정을 로드합니다.

        Args:
            config_path: config.yaml 파일 경로

        Returns:
            AppConfig 인스턴스

        Raises:
            FileNotFoundError: 설정 파일이 존재하지 않는 경우
            ValidationError: 설정이 유효하지 않은 경우
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(
                f"설정 파일을 찾을 수 없습니다: {config_path}. "
                f"config.yaml.example을 참고하여 설정 파일을 생성하세요."
            )

        with open(config_file, encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        return AppConfig(**config_data)
