from django.db import models


class Dataset(models.Model):

    DATASET_TYPES = [
        ("customers", "Customers"),
        ("products", "Products"),
        ("orders", "Orders"),
        ("order_items", "Order Items"),
        ("payments", "Payments"),
        ("returns", "Returns"),
        ("marketing", "Marketing"),
        ("expenses", "Expenses"),
    ]

    name = models.CharField(
        max_length=255
    )

    dataset_type = models.CharField(
        max_length=50,
        choices=DATASET_TYPES
    )

    file = models.FileField(
        upload_to="datasets/"
    )

    file_size = models.PositiveBigIntegerField(
        default=0
    )

    row_count = models.PositiveIntegerField(
        default=0
    )

    column_count = models.PositiveIntegerField(
        default=0
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.name} ({self.get_dataset_type_display()})"

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"