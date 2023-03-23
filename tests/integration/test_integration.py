#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the lte-controller rock.

These tests assume that the lte-controller container is running and available at the url:port
defined below.
"""

import requests  # type: ignore[import]

import unittest

LTE_CONTROLLER_DOCKER_URL = 'http://localhost'
LTE_CONTROLLER_DOCKER_PORT = 8080


class TestLTEControllerRock(unittest.TestCase):
    """Integration tests for the lte-controller rock."""

    def test_given_lte_controller_container_is_running_when_http_get_then_hello_message_is_returned(  # noqa: E501
        self
    ):
        response = requests.get(f"{LTE_CONTROLLER_DOCKER_URL}:{LTE_CONTROLLER_DOCKER_PORT}")

        assert response.status_code == 404
        assert "Not Found" in response.text
