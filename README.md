# Aiogram bot template

## Requirements
* `python 3.11<=`
* `aiogram 2`
* `redis` Optional
* `docker` Optional

## Install and run
1. Clone project
    ```shell
   # https
   git clone https://github.com/SaD-Pr0gEr/aiogram-template.git

   # ssh
   git clone git@github.com:SaD-Pr0gEr/aiogram-template.git
    ```
2. Rename project name/description in `pyproject.toml`
3. Install dependencies and activate poetry shell
    ```shell
    poetry install && poetry shell
    ```
4. Copy `.env.dist` as `.env` and set all values
5. Run `python bot.py`
