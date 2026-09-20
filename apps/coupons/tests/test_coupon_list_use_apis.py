import datetime

import pytest
from django.utils import timezone

from apps.coupons.models import BoothVerifyCode, Coupon, User

COUPON_LIST_URL = "/api/coupons/"


def use_url(coupon_id):
    return f"/api/coupons/{coupon_id}/use/"


@pytest.mark.django_db
class TestCouponListAPI:
    def test_unauthorized_without_user(self, client):
        response = client.get(COUPON_LIST_URL)
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "UNAUTHORIZED"

    def test_empty_list(self, client):
        user = User.objects.create(name="유저1")
        response = client.get(COUPON_LIST_URL, {"user": user.id})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 0
        assert data["data"]["items"] == []

    def test_list_returns_own_coupons(self, client):
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user,
            issued_date=timezone.localdate(),
            daily_sequence=1,
            status=Coupon.Status.WIN,
        )

        response = client.get(COUPON_LIST_URL, {"user": user.id})
        assert response.status_code == 200
        items = response.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["coupon_id"] == coupon.coupon_id
        assert items[0]["status"] == "WIN"

    def test_status_filter(self, client):
        user = User.objects.create(name="유저1")
        yesterday = timezone.localdate() - datetime.timedelta(days=1)
        Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )
        Coupon.objects.create(
            user=user, issued_date=yesterday, daily_sequence=1, status=Coupon.Status.LOSE
        )

        response = client.get(COUPON_LIST_URL, {"user": user.id, "status": "WIN"})
        items = response.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["status"] == "WIN"


@pytest.mark.django_db
class TestCouponUseAPI:
    def test_missing_verify_code(self, client):
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )

        response = client.post(
            use_url(coupon.coupon_id), {"user": user.id}, content_type="application/json"
        )
        assert response.status_code == 400
        assert response.json()["code"] == "INVALID_INPUT"

    def test_nonexistent_user(self, client):
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )

        response = client.post(
            use_url(coupon.coupon_id),
            {"user": 999999, "verify_code": "aaa"},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert response.json()["code"] == "INVALID_INPUT"

    def test_wrong_verify_code(self, client):
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )

        response = client.post(
            use_url(coupon.coupon_id),
            {"user": user.id, "verify_code": "WRONG"},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert response.json()["code"] == "INVALID_VERIFY_CODE"

    def test_use_success(self, client):
        BoothVerifyCode.objects.create(code="lovelion14")
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )

        response = client.post(
            use_url(coupon.coupon_id),
            {"user": user.id, "verify_code": "lovelion14"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "COUPON_USE_SUCCESS"
        assert data["data"]["status"] == "USED"

        coupon.refresh_from_db()
        assert coupon.status == Coupon.Status.USED
        assert coupon.used_at is not None

    def test_use_already_used(self, client):
        BoothVerifyCode.objects.create(code="lovelion14")
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )

        first = client.post(
            use_url(coupon.coupon_id),
            {"user": user.id, "verify_code": "lovelion14"},
            content_type="application/json",
        )
        assert first.status_code == 200

        second = client.post(
            use_url(coupon.coupon_id),
            {"user": user.id, "verify_code": "lovelion14"},
            content_type="application/json",
        )
        assert second.status_code == 409
        assert second.json()["code"] == "COUPON_ALREADY_USED"

    def test_use_not_win(self, client):
        BoothVerifyCode.objects.create(code="lovelion14")
        user = User.objects.create(name="유저1")
        coupon = Coupon.objects.create(
            user=user, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.LOSE
        )

        response = client.post(
            use_url(coupon.coupon_id),
            {"user": user.id, "verify_code": "lovelion14"},
            content_type="application/json",
        )
        assert response.status_code == 409
        assert response.json()["code"] == "COUPON_NOT_WIN"

    def test_use_expired(self, client):
        BoothVerifyCode.objects.create(code="lovelion14")
        user = User.objects.create(name="유저1")
        yesterday = timezone.localdate() - datetime.timedelta(days=1)
        coupon = Coupon.objects.create(
            user=user, issued_date=yesterday, daily_sequence=1, status=Coupon.Status.WIN
        )

        response = client.post(
            use_url(coupon.coupon_id),
            {"user": user.id, "verify_code": "lovelion14"},
            content_type="application/json",
        )
        assert response.status_code == 409
        assert response.json()["code"] == "COUPON_EXPIRED"

    def test_cannot_use_other_users_coupon(self, client):
        BoothVerifyCode.objects.create(code="lovelion14")
        owner = User.objects.create(name="주인")
        stranger = User.objects.create(name="타인")
        coupon = Coupon.objects.create(
            user=owner, issued_date=timezone.localdate(), daily_sequence=1, status=Coupon.Status.WIN
        )

        response = client.post(
            use_url(coupon.coupon_id),
            {"user": stranger.id, "verify_code": "lovelion14"},
            content_type="application/json",
        )
        assert response.status_code == 409
        assert response.json()["code"] == "COUPON_NOT_USABLE"
