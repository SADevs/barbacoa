# -*- coding: utf-8 -*-
import pytest

import barbacoa.hub.struct


@pytest.fixture
def hub():
    return barbacoa.hub.struct.Hub()
