This is a script created for data gathering compatible with the TOPS script created in my master's thesis. This script in based on the example provided by Sigurd Hofsmo Jakobsen in Gitlab (https://gitlab.sintef.no/power-system-asset-management/opne-kodesnuttar/entso-e-transparency-platform-api).

From original readme file:
## Getting access to the platform
To get access to the platform an API-key is needed. It can easily be obtained by following this guide https://amsleser.no/blog/post/21-obtaining-api-token-from-entso-e .

## Installing example
All the dependencies of the example are listed in the .pyproject.toml file. The easiest way to install the example is to use the tool [pdm](https://pdm.fming.dev/latest/) and run the command `pdm update`.

## Running the example
The example is stored in a Python lightscript and can be run as any Python script. For handling the API key, a file named ".env" should be created and contain the key on the format `api_key="your-key"`. The script will automatically load the key and use it for acccessing the API.

With pdm the script can easily be loaded as a notebook using the command `pdm run lab` in linux. In Windows the command is `pdm run .venv/Scripts/jupyter-lab`.
