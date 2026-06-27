from django.conf import settings
from django.db import models


class PropertyCategory(models.TextChoices):
    HOUSE = "house", "House"
    APARTMENT = "apartment", "Apartment"
    VILLA = "villa", "Villa"
    COMMERCIAL = "commercial", "Commercial Building"
    OFFICE = "office", "Office"
    LAND = "land", "Land"


class ListingStatus(models.TextChoices):
    BUY = "buy", "Buy"
    RENT = "rent", "Rent"


class Amenity(models.Model):
    """Master list of amenities. Admin manages these; properties M2M into them."""

    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="lucide-react icon name")

    class Meta:
        verbose_name_plural = "amenities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Property(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=14, decimal_places=2)
    listing_status = models.CharField(max_length=10, choices=ListingStatus.choices, default=ListingStatus.BUY)
    property_type = models.CharField(max_length=20, choices=PropertyCategory.choices)

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    parking = models.PositiveIntegerField(default=0)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="square feet/meters")

    amenities = models.ManyToManyField(Amenity, blank=True, related_name="properties")

    is_featured = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    agent = models.ForeignKey(
        "agents.Agent", on_delete=models.SET_NULL, null=True, blank=True, related_name="properties"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_properties"
    )

    views_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "properties"
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["property_type"]),
            models.Index(fields=["listing_status"]),
            models.Index(fields=["is_featured"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base = slugify(self.title)[:260]
            slug = base
            counter = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/images/")
    caption = models.CharField(max_length=255, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="videos")
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to="properties/videos/", blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Video for {self.property.title}"


class FloorPlan(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="floor_plans")
    image = models.ImageField(upload_to="properties/floor_plans/")
    title = models.CharField(max_length=255, blank=True)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Floor plan for {self.property.title}"


class PropertyDocument(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="properties/documents/")
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_searches")
    name = models.CharField(max_length=120, blank=True)
    query_params = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} saved search #{self.pk}"


class RecentSearch(models.Model):
    """Lightweight log of recent free-text searches per user, for the 'recent searches' UI."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recent_searches")
    keyword = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class RecentlyViewed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recently_viewed")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="viewed_by")
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-viewed_at"]
        unique_together = ("user", "property")


class PropertyComparison(models.Model):
    """Holds up to 4 properties a user is actively comparing."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comparisons")
    properties = models.ManyToManyField(Property, related_name="comparisons")
    created_at = models.DateTimeField(auto_now_add=True)
