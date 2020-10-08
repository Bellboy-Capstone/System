# System

![CI](https://github.com/Bellboy-Capstone/System/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4150c01ff4e54051a6d930103ea02747)](https://www.codacy.com/gh/Bellboy-Capstone/System/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Bellboy-Capstone/System&amp;utm_campaign=Badge_Grade)

Embedded Raspberry Pi Program

## Usage
```sh
cd System/bellboy
python bellboy [-h]
```
Status: only prints some logs.
Change log verbosity on cmd line like this
```sh
python bellboy loglevel
```
loglevel can be INFO, DEBUG, WARNING or ERROR

## Development

```sh
# Install dependencies (if on Win10 use admin powershell)
pip install -r requirements/REQUIRMEMENTS.txt

# Activate pre-commit, it'll check your files for mistakes before you commit
pre-commit install
```

## Resources

1. [Actor tutorial w/Thespian](https://bytes.yingw787.com/posts/2019/02/02/concurrency_with_python_actor_models/)
1. [Thespian docs](https://thespianpy.com/doc/)
