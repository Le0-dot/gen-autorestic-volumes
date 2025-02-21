import shutil
from pathlib import Path
from operator import or_
from typing import Any, Iterable
from functools import reduce, partial

import docker
import yaml


def list_docker_volumes(
    client: docker.client.DockerClient = docker.from_env(),
) -> Iterable[str]:
    volumes = client.volumes.list()
    predicate = (
        lambda volume: "com.docker.volume.anonymous" not in volume.attrs["Labels"]
    )
    get_name = lambda volume: volume.name
    return map(get_name, filter(predicate, volumes))


def make_volume_location(volume: str, to: Iterable[str]) -> dict[str, dict[str, Any]]:
    return {
        volume: {
            "from": volume,
            "to": list(to),
            "type": "volume",
        }
    }


def create_config() -> Path:
    config = Path(".autorestic.yml")
    config_backup = Path(".autorestic.yml.bak")
    config_template = Path(".autorestic.yml.template")

    if config.exists():
        shutil.move(config, config_backup)
    shutil.copy(config_template, config)

    return config


def main() -> None:
    volumes = list_docker_volumes()
    make_location = partial(make_volume_location, to=["ssd", "gdrive"])
    volume_locations = reduce(or_, map(make_location, volumes))
    location = {"locations": volume_locations}

    config = create_config()

    with config.open(mode="a") as file:
        yaml.dump(location, file)


if __name__ == "__main__":
    main()
