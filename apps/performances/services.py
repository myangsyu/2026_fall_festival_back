"""공연 도메인 판정 로직."""

from django.conf import settings

from .constants import NOW_PLAYING_LIMIT, UPCOMING_PREVIEW_WINDOW
from .selectors import list_live, list_upcoming_on


def is_live(performance, now):
    """현재 공연 진행 여부를 반환한다."""
    return performance.start_at <= now < performance.end_at


def resolve_festival_date(requested_date, today):
    """타임테이블 조회에 사용할 날짜를 결정한다."""
    if requested_date is not None:
        return requested_date

    if settings.FESTIVAL_START_DATE <= today <= settings.FESTIVAL_END_DATE:
        return today

    return settings.FESTIVAL_START_DATE


def now_playing_performances(now, limit=NOW_PLAYING_LIMIT):
    live = list_live(now)

    # ① 현재 공연 중인 게 있을 때
    if live:
        festival_date = live[0].festival_date

        # 진행 중 공연만으로 최대 개수 이상이면
        # 예정 공연 조회할 필요 없음
        if len(live) >= limit:
            return live[:limit]

        # 남은 자리만큼 예정 공연 추가
        upcoming = list_upcoming_on(
            festival_date,
            now,
            limit - len(live),
        )

        return (live + upcoming)[:limit]

    # ② 현재 공연 중인 게 하나도 없을 때
    festival_date = resolve_festival_date(None, now.date())
    upcoming = list_upcoming_on(festival_date, now, limit)

    if not upcoming:
        return []

    # 다음 공연이 1시간 이내면 미리보기
    if upcoming[0].start_at - now <= UPCOMING_PREVIEW_WINDOW:
        return upcoming

    return []
