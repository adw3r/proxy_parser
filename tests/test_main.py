import os
import configparser
import pytest

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")


def test_config_file_exists():
    assert os.path.exists(CONFIG_PATH), f"Config file not found at {CONFIG_PATH}"


def test_config_general_section():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    assert "General" in config, "Missing [General] section in config.ini"


def test_config_general_keys():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    general = config["General"]
    required_keys = [
        "Timeout",
        "MaxConnections",
        "SavePath",
        "MainTimeout",
        "ParsingDepth",
    ]
    for key in required_keys:
        assert key in general, f"Missing key '{key}' in [General] section"


def test_config_timeout_values_are_int():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    general = config["General"]
    int_keys = ["Timeout", "MaxConnections", "MainTimeout", "ParsingDepth"]
    for key in int_keys:
        value = general.get(key)
        assert value is not None, f"Key '{key}' missing in [General]"
        try:
            int(value)
        except ValueError:
            pytest.fail(f"Value for '{key}' is not an integer: {value}")


def test_config_savepath_is_valid():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    save_path = config["General"].get("SavePath")
    assert save_path, "SavePath is not set in config.ini"
    # Accept both with and without trailing slash
    dir_path = save_path.rstrip("\\/")
    # Check that the path is not empty and is a valid path
    assert len(dir_path) > 0, "SavePath is empty"
    # Directory may not exist yet, so just check it's a plausible path
    assert not dir_path.startswith("//"), "SavePath should not start with //"
