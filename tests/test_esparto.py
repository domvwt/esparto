#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `esparto` package."""

import pytest

import esparto as es

print("Using pytest version:", pytest.__version__)


def test_minimal():
    assert es.__version__ == "0.1.0"
