import pytest

from ckanext.og_datatablesview.helpers import version_builder
from packaging.version import InvalidVersion


def test_version_builder_positive():
    assert version_builder('2.7') < version_builder('2.9')
    assert version_builder('2.7.1') < version_builder('2.7.2')
    assert version_builder('2.7.10') < version_builder('2.7.11')
    assert version_builder('2.7.1') < version_builder('2.9.2.3')
    assert version_builder('2.7.1') < version_builder('2.7.10')
    assert version_builder('2.7.10') < version_builder('2.9.1')


def test_version_builder_failed_to_build():
    with pytest.raises(InvalidVersion):
        assert version_builder('1.3.xy123')