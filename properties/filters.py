import django_filters as filters

from .models import Property


class PropertyFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_area = filters.NumberFilter(field_name="area_size", lookup_expr="gte")
    max_area = filters.NumberFilter(field_name="area_size", lookup_expr="lte")
    bedrooms = filters.NumberFilter(field_name="bedrooms", lookup_expr="gte")
    bathrooms = filters.NumberFilter(field_name="bathrooms", lookup_expr="gte")
    city = filters.CharFilter(field_name="city", lookup_expr="icontains")
    property_type = filters.CharFilter(field_name="property_type")
    listing_status = filters.CharFilter(field_name="listing_status")
    amenities = filters.BaseInFilter(field_name="amenities__id", lookup_expr="in")
    is_featured = filters.BooleanFilter(field_name="is_featured")
    is_sold = filters.BooleanFilter(field_name="is_sold")

    class Meta:
        model = Property
        fields = [
            "min_price", "max_price", "min_area", "max_area", "bedrooms", "bathrooms",
            "city", "property_type", "listing_status", "amenities", "is_featured", "is_sold",
        ]
