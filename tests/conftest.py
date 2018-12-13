# -*- coding: utf-8 -*-
import pytest

import barbacoa


@pytest.fixture
def hub():
    return barbacoa.hub
