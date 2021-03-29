#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `esparto` package."""

import pytest
import esparto as es

def test_minimal():
    assert es.__version__ == "0.1.0"
