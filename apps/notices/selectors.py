"""Notices data selectors."""

from django.db.models import Case, QuerySet, Value, When

from apps.notices.models import Notice


def get_admin_notices_queryset(notice_type: str = "ALL") -> QuerySet[Notice]:
    """관리자용 공지사항 목록 쿼리셋을 반환

    - 삭제되지 않은(alive) 공지만 조회
    - 긴급(URGENT) 공지 최우선 노출
    - 동일 우선순위 내 최신순(created_at desc) 정렬
    - type 필터 지원 (ALL, URGENT, NORMAL)
    """
    queryset = Notice.objects.alive()

    if notice_type in (Notice.Type.URGENT, Notice.Type.NORMAL):
        queryset = queryset.filter(type=notice_type)

    return queryset.annotate(
        type_priority=Case(
            When(type=Notice.Type.URGENT, then=Value(0)),
            When(type=Notice.Type.NORMAL, then=Value(1)),
            default=Value(2),
        )
    ).order_by("type_priority", "-created_at", "-id")


def get_notice_by_id(notice_id: int) -> Notice | None:
    """ID로 삭제되지 않은 공지사항 단건을 조회합니다."""
    return Notice.objects.alive().filter(pk=notice_id).first()


    def get_notices_queryset(notice_type: str = "ALL") -> QuerySet[Notice]:
    """사용자용 공지사항 목록 쿼리셋을 반환 (긴급 우선 -> 최신순)"""
    return get_admin_notices_queryset(notice_type=notice_type)