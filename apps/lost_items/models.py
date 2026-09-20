"""Lost items database models."""

from django.db import models

from common.models import SoftDeleteModel


class LostItem(SoftDeleteModel):
    """A single lost-and-found post registered by an administrator."""

    lost_item_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    found_date = models.DateField()

    # TODO(admins): becomes FK("admins.Admin") once the admin model is merged.
    created_by_admin_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "lost_item"
        ordering = ["-created_at", "-lost_item_id"]
        indexes = [
            models.Index(fields=["deleted_at", "found_date"]),
            models.Index(fields=["deleted_at", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.lost_item_id}] {self.title}"


class LostItemImage(SoftDeleteModel):
    """Image attached to a lost item. Array order becomes ``sort_order``."""

    image_id = models.BigAutoField(primary_key=True)
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500)
    sort_order = models.PositiveIntegerField()

    class Meta:
        db_table = "lost_item_image"
        ordering = ["sort_order", "image_id"]
        indexes = [models.Index(fields=["lost_item", "deleted_at", "sort_order"])]

    def __str__(self):
        return f"{self.lost_item_id}#{self.sort_order}"


class LostItemTag(SoftDeleteModel):
    """Keyword chip. Array order becomes ``sort_order``."""

    tag_id = models.BigAutoField(primary_key=True)
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, related_name="tags")
    keyword = models.CharField(max_length=30)
    sort_order = models.PositiveIntegerField()

    class Meta:
        db_table = "lost_item_tag"
        ordering = ["sort_order", "tag_id"]
        indexes = [models.Index(fields=["lost_item", "deleted_at", "sort_order"])]

    def __str__(self):
        return self.keyword
