import tomllib


def get_default_config(keys: list[str] | None = None) -> dict:
    DEFAULT_CONFIG_PATH = 'lib/googlepy/asserts/config/default.toml'
    if not DEFAULT_CONFIG_PATH:
        raise FileNotFoundError(f"Default config file not found at {DEFAULT_CONFIG_PATH}")
    with open(DEFAULT_CONFIG_PATH, "rb") as f:
        data = tomllib.load(f)
    if keys:
        for key in keys:
            if key not in data:
                raise KeyError(f"Key '{key}' not found in default config")
            data = data[key]
    return data
