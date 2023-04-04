#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the lte-controller rock.

These tests assume that the lte-controller container is running and available at the url:port
defined below.
"""

import logging

import glob
import subprocess
import unittest
from time import sleep, time

import docker
import requests  # type: ignore[import]
import yaml

ROCKCRAFT_FILE_PATH = "../rockcraft.yaml"

LTE_CONTROLLER_DOCKER_URL = "http://localhost"
LTE_CONTROLLER_DOCKER_PORT = 8080

POSTGRES_USER = "username"
POSTGRES_PASSWORD = "password"
POSTGRES_DB = "magma"

logger = logging.getLogger(__name__)

class TestLTEControllerRock(unittest.TestCase):
    """Integration tests for the lte-controller rock."""

    def setUp(self):
        """Runs containers under test."""

        self._move_rock_to_docker_registry()

        self.client = docker.from_env()
        self.network = self.client.networks.create(
            "bridge_network",
            driver="bridge",
        )
        
        self._run_postgres_container()
        
        timeout = 15
        start_time = time()
        while (time() - start_time) < timeout:
            if not self._postgres_ready():
                sleep(1)
            else:
                self._run_orc8r_lte_controller_container()
                return
        raise TimeoutError("Postgres container is not ready after 15 seconds.")
    
    @staticmethod
    def _get_image_name_and_version() -> tuple:
        """Fetches image name and version from rockcraft.yaml."""
        with open(ROCKCRAFT_FILE_PATH, "r") as file:
            data = yaml.safe_load(file)
            image_name = data["name"]
            version = data["version"]
        return (image_name, version)
    
    @property
    def _host_ip(self) -> str:
        """Fetches postgres host IP address from docker container."""
        container = self.client.containers.get('postgres_container')
        ip_address = list(container.attrs['NetworkSettings']['Networks'].values())[0]['IPAddress']
        return ip_address
    
    def _postgres_ready(self):
        """Checks if postgres is ready to accept connections by checking the logs."""
        container = self.client.containers.get('postgres_container')
        logs = container.logs().decode('utf-8')

        return "database system is ready to accept connections" in logs
        
    def _move_rock_to_docker_registry(self):
        image_name, version = self._get_image_name_and_version()
        rock_file = glob.glob("../../**/*.rock", recursive=True).pop()
        
        subprocess.run(
            [
                "sudo",
                "skopeo",
                "--insecure-policy",
                "copy",
                f"oci-archive:{rock_file}",
                f"docker-daemon:ghcr.io/canonical/{image_name}:{version}",
            ],
            check=True,
        )
        
    def _run_postgres_container(self):
        postgres_container = self.client.containers.run(
            "postgres",
            detach=True,
            ports={"5432/tcp": 5432},
            environment={
                "POSTGRES_USER": POSTGRES_USER,
                "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
                "POSTGRES_DB": POSTGRES_DB,
            },
            name="postgres_container",
        )
        self.network.connect(postgres_container)
        
    def _run_orc8r_lte_controller_container(self):
        image_name, version = self._get_image_name_and_version()
        database_source = f"dbname=magma user=username password=password host={self._host_ip} sslmode=disable"
        
        orc8r_lte_controller_container = self.client.containers.run(
            f"ghcr.io/canonical/{image_name}:{version}",
            detach=True,
            ports={"10113/tcp": 8080},
            environment={
             "DATABASE_SOURCE": database_source
            },
            name = "orc8r_lte_controller_container",
        )
        self.network.connect(orc8r_lte_controller_container)

    def test_given_lte_controller_container_is_running_when_http_get_then_hello_message_is_returned(  # noqa: E501
        self,
    ):
        """Test to validate that the container is running correctly."""
        url = f"{LTE_CONTROLLER_DOCKER_URL}:{LTE_CONTROLLER_DOCKER_PORT}"
        for _ in range(30):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 404:
                    break
            except Exception as e:
                logger.error(e)
            sleep(1)
        else:
            assert False, "Failed to get a 404 response within 30 seconds."
