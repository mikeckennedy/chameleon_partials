# Testing placeholder. We should write some tests.
from pathlib import Path

# noinspection PyPackageRequirements
import pytest as pytest

import chameleon_partials


@pytest.fixture
def registered_extension():
    folder = (Path(__file__).parent / "test_templates").as_posix()
    chameleon_partials.register_extensions(folder, auto_reload=True, cache_init=True)

    # Allow test to work with extensions as registered
    yield

    # Roll back the fact that we registered the extensions for future tests.
    chameleon_partials.has_registered_extensions = False


def test_render_empty(registered_extension):
    assert True, "dummy sample test"
