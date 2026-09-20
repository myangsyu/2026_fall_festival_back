"""Tests for user lost items API."""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APITestCase

from apps.lost_items.models import LostItem, LostItemImage, LostItemTag


@pytest.mark.django_db
class TestUserLostItemAPI(APITestCase):
    def setUp(self):
        # 1. 분실물 1 (검색/필터 대상)
        self.item1 = LostItem.objects.create(
            title="대운동장 휴대폰케이스",
            found_date=date(2026, 9, 29),
        )
        self.img1 = LostItemImage.objects.create(
            lost_item=self.item1,
            image_url="https://cdn.example.com/lost/case1.jpg",
            sort_order=1,
        )
        self.img2 = LostItemImage.objects.create(
            lost_item=self.item1,
            image_url="https://cdn.example.com/lost/case2.jpg",
            sort_order=2,
        )
        self.tag1 = LostItemTag.objects.create(
            lost_item=self.item1, keyword="휴대폰케이스", sort_order=1
        )
        self.tag2 = LostItemTag.objects.create(lost_item=self.item1, keyword="검정색", sort_order=2)
        self.tag3 = LostItemTag.objects.create(
            lost_item=self.item1, keyword="아이폰14pro", sort_order=3
        )
        self.tag4 = LostItemTag.objects.create(
            lost_item=self.item1, keyword="대운동장", sort_order=4
        )

        # 2. 분실물 2
        self.item2 = LostItem.objects.create(
            title="학생회관 지갑",
            found_date=date(2026, 9, 30),
        )

    def test_list_lost_items_success(self):
        response = self.client.get("/api/lost-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], "LOST_ITEM_LIST_SUCCESS")
        self.assertEqual(len(response.data["data"]["items"]), 2)

    def test_list_lost_items_filtering(self):
        res_date = self.client.get("/api/lost-items/", {"found_date": "2026-09-29"})
        self.assertEqual(len(res_date.data["data"]["items"]), 1)

        res_kw = self.client.get("/api/lost-items/", {"keyword": "검정색"})
        self.assertEqual(len(res_kw.data["data"]["items"]), 1)

    def test_list_lost_items_invalid_date(self):
        response = self.client.get("/api/lost-items/", {"found_date": "2026-99-99"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "INVALID_INPUT")

    def test_detail_lost_item_success(self):
        response = self.client.get(f"/api/lost-items/{self.item1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["lost_item_id"], self.item1.pk)
        self.assertEqual(len(response.data["data"]["tags"]), 4)

    def test_detail_lost_item_not_found(self):
        response = self.client.get("/api/lost-items/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["code"], "LOST_ITEM_NOT_FOUND")
