"""
CLI 래퍼

sys.path를 설정하여 src 패키지를 임포트 가능하게 합니다.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from main import app


def main() -> None:
    app()
