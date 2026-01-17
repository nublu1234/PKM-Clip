"""
로깅 설정 모듈

loguru를 사용하여 로그 시스템을 설정합니다.
stderr 출력과 파일 저장을 지원하며, 파일은 30일마다 회전합니다.
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(verbose: bool = False) -> None:
    """
    로거를 설정합니다.

    Args:
        verbose: True인 경우 DEBUG 레벨로 설정, 기본값은 INFO
    """
    logger.remove()

    level = "DEBUG" if verbose else "INFO"

    logger.add(
        sys.stderr,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
        colorize=True,
    )

    log_dir = Path.home() / ".pkm-clip" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"
    logger.add(
        log_file,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
        rotation="30 days",
        retention="30 days",
        compression="zip",
    )


def get_logger() -> logger:
    """
    설정된 로거 인스턴스를 반환합니다.

    Returns:
        loguru Logger 인스턴스
    """
    return logger
