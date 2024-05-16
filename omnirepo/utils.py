import json
import shutil
import os
from pathlib import Path
import tomli
import tomli_w


def get_config() -> dict | None:
    """
    Reads omnirepo.json config file from workspace root. Returns None if no config was found.
    :return:
    """
    try:
        f = open("omnirepo-config.json")
        config = json.load(f)
        f.close()
        return config
    except FileNotFoundError:
        return None


def update_config(config: dict) -> None:
    with open("omnirepo-config.json", "r+") as f:
        f.seek(0)
        json_serialized = json.dumps(config, indent=2)
        f.write(json_serialized)
        f.truncate()


def get_pyproject_toml() -> dict:
    with open("pyproject.toml", mode="rb") as fp:
        return tomli.load(fp)


def update_pyproject_toml(updated: dict) -> None:
    f = open("pyproject.toml", "w")
    config = tomli_w.dumps(updated)
    f.write(config)
    f.close()


def get_vscode_settings() -> dict | None:
    try:
        f = open(".vscode/settings.json")
        settings = json.load(f)
        f.close()
        return settings
    except FileNotFoundError:
        return None


def update_vscode_settings(settings: dict) -> None:
    with open(".vscode/settings.json", "r+") as f:
        f.seek(0)
        json_serialized = json.dumps(settings, indent=2)
        f.write(json_serialized)
        f.truncate()


def mkdir_if_not_exists(path):
    """
    Creates directory at the specified path if it does not exist. Adds parent directories along path if necessary.
    :param path:
    :return:
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def check_dir_exists(path) -> bool:
    return os.path.exists(path)


def rmdir_if_exists(path):
    shutil.rmtree(path, ignore_errors=True)


def write_string_to_file(string: str, path: str) -> None:
    """
    Writes string to file. Overwrites existing file if it exists. Creates directories along the way if needed.
    :param string:
    :param path:
    :return:
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.isfile(path):
        with open(path, "r+") as f:
            f.seek(0)
            f.write(string)
            f.truncate()
    else:
        with open(path, "w") as f:
            f.write(string)


def infer_author():
    """
    Get author name from git
    :return:
    """
    pass


# def replace_hyphen_with_underscores(string: str) -> str:
#     pass


def get_template_paths(templates_file_path) -> list:
    """
    Read templates to be created and populated from the template set's templates.txt file
    """
    with open(templates_file_path, "r") as file:
        return file.read().split("\n")


def get_project_directory(project_name):
    config = get_config()
    dir = [d for d in config['packages'] if project_name in config['packages'][d]]
    return dir[0] if len(dir) > 0 else None
