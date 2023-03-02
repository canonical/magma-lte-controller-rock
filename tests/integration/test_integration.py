#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the orc8r-controller rock.

These tests assume that the orc8r-controller container is running and available at the url:port
defined below.
"""

import requests  # type: ignore[import]

import unittest

ORC8R_CONTROLLER_DOCKER_URL = 'http://localhost'
ORC8R_CONTROLLER_DOCKER_PORT = 8080


class TestOrc8rControllerRock(unittest.TestCase):
    """Integration tests for the orc8r-controller rock."""

    def test_given_orc8r_controller_container_is_running_when_http_get_then_hello_message_is_returned(  # noqa: E501
        self
    ):
        response = requests.get(f"{ORC8R_CONTROLLER_DOCKER_URL}:{ORC8R_CONTROLLER_DOCKER_PORT}")

        assert response.status_code == 200
        assert "hello" in response.text
