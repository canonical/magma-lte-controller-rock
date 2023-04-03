#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the lte-controller rock.

These tests assume that the lte-controller container is running and available at the url:port
defined below.
"""

import glob
import os
import subprocess
import unittest

import requests  # type: ignore[import]
import yaml

ROCKCRAFT_FILE_PATH = "../rockcraft.yaml"
LTE_CONTROLLER_DOCKER_URL = "http://localhost"
LTE_CONTROLLER_DOCKER_PORT = 8080


class TestLTEControllerRock(unittest.TestCase):
    """Integration tests for the lte-controller rock."""

    def setUp(self):
        with open(ROCKCRAFT_FILE_PATH, "r") as file:
            data = yaml.safe_load(file)
            self.image_name = data["name"]
            self.version = data["version"]

        rock_file = glob.glob("../../**/*.rock", recursive=True).pop()
        subprocess.run(
            [
                "sudo",
                "skopeo",
                "--insecure-policy",
                "copy",
                f"oci-archive:{rock_file}",
                f"docker-daemon:ghcr.io/canonical/{self.image_name}:{self.version}",
            ],
            check=True,
        )

        os.environ["POSTGRES_USER"] = "username"
        os.environ["POSTGRES_PASSWORD"] = "password"
        os.environ["POSTGRES_DB"] = "magma"
        os.environ[
            "DATABASE_SOURCE"
        ] = "dbname=magma user=username password=password host=172.17.0.2 sslmode=disable"

        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "-p",
                "5432:5432",
                "--env",
                "POSTGRES_PASSWORD",
                "--env",
                "POSTGRES_USER",
                "--env",
                "POSTGRES_DB",
                "--network",
                "bridge",
                "postgres",
            ],
            check=True,
        )
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "-p",
                "8080:10112",
                "--network",
                "bridge",
                f"ghcr.io/canonical/{self.image_name}:{self.version}",
            ],
            check=True,
        )

    def test_given_lte_controller_container_is_running_when_http_get_then_hello_message_is_returned(  # noqa: E501
        self,
    ):
        response = requests.get(f"{LTE_CONTROLLER_DOCKER_URL}:{LTE_CONTROLLER_DOCKER_PORT}")

        assert response.status_code == 404
        assert "Not Found" in response.text
