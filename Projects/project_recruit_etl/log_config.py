"""중앙 로깅 설정 모듈.

파이프라인 전체에서 일관된 포맷·레벨·출력 대상을 사용한다.
각 모듈에서 get_logger(__name__)을 호출해 모듈 전용 로거를 생성한다.
"""

import logging
import logging.handlers
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_FMT = logging.Formatter(
    "%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
    """모듈 이름으로 로거를 생성한다.

    - StreamHandler: INFO 이상을 콘솔에 출력
    - TimedRotatingFileHandler: DEBUG 이상을 파일에 기록, 자정마다 로테이션, 7일 보관
    - propagate=False: 루트 로거로 전파하지 않아 중복 출력을 방지
    """
    logger = logging.getLogger(name)

    if logger.handlers:     # 같은 이름으로 중복 호출 시 재사용
        return logger

    logger.setLevel(logging.DEBUG)

    # 콘솔 — INFO 이상
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_FMT)
    logger.addHandler(ch)

    # 파일 — DEBUG 이상, 자정마다 새 파일, 최대 7일치 보관
    fh = logging.handlers.TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "pipeline.log"),
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FMT)
    logger.addHandler(fh)

    logger.propagate = False
    return logger
