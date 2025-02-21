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

    if not config_template.exists():
        raise RuntimeError(f"counld not find {config_template}")

    if config.exists():
        shutil.move(config, config_backup)
    shutil.copy(config_template, config)

    return config


def main() -> None:
    config = create_config()

    with config.open(mode="r") as file:
        autorestic_config = yaml.safe_load(file)

    backends = autorestic_config["backends"].keys()
    
    volumes = list_docker_volumes()
    make_location = partial(make_volume_location, to=backends)
    volume_locations = reduce(or_, map(make_location, volumes))

    autorestic_config["locations"] = autorestic_config.get("locations", {}) | volume_locations

    with config.open(mode="w") as file:
        yaml.dump(autorestic_config, file)


if __name__ == "__main__":
    main()
