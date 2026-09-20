"""Public lost items API routes (user side)."""

from django.urls import path

from .views import UserLostItemDetailView, UserLostItemListView

app_name = "lost_items"

urlpatterns = [
    # 사용자 분실물 목록 조회: GET /api/lost-items/
    path("", UserLostItemListView.as_view(), name="list"),
    # 사용자 분실물 상세 조회: GET /api/lost-items/<id>/
    path("<int:lost_item_id>/", UserLostItemDetailView.as_view(), name="detail"),
]
