"""
Shared DRF serializer fields.

DRF's built-in `FileField`/`ImageField.to_representation` unconditionally
calls `request.build_absolute_uri(value.url)` whenever a `request` is
present in the serializer context. That's correct for local
`FileSystemStorage`, where `value.url` is a relative path like
`/media/foo.jpg` — but it's WRONG for Cloudinary (or any storage backend
that already returns a fully-qualified absolute URL), because it prepends
our own domain in front of the Cloudinary URL, producing a broken link
like:

    https://aurelia-backend-h797.onrender.com/https://res.cloudinary.com/...

`SafeFileField`/`SafeImageField` below only call `build_absolute_uri` when
`value.url` is NOT already absolute, fixing this for every serializer that
uses them.
"""

from rest_framework import serializers


class SafeFileFieldMixin:
    def to_representation(self, value):
        if not value:
            return None

        use_url = getattr(self, "use_url", None)
        if use_url is None:
            from rest_framework.settings import api_settings

            use_url = api_settings.UPLOADED_FILES_USE_URL

        if not use_url:
            return value.name

        try:
            url = value.url
        except AttributeError:
            return None

        if url.startswith("http://") or url.startswith("https://"):
            return url

        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class SafeFileField(SafeFileFieldMixin, serializers.FileField):
    pass


class SafeImageField(SafeFileFieldMixin, serializers.ImageField):
    pass
