import pytest


@pytest.fixture(autouse=True)
def test_runtime_settings(settings):
    settings.CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pytest-cache",
    }
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.db"
