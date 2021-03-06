# System

![CI](https://github.com/Bellboy-Capstone/System/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4150c01ff4e54051a6d930103ea02747)](https://www.codacy.com/gh/Bellboy-Capstone/System/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Bellboy-Capstone/System&amp;utm_campaign=Badge_Grade)
[![Updates](https://pyup.io/repos/github/Bellboy-Capstone/System/shield.svg)](https://pyup.io/repos/github/Bellboy-Capstone/System/)
[![Python
3](https://pyup.io/repos/github/Bellboy-Capstone/System/python-3-shield.svg)](https://pyup.io/repos/github/Bellboy-Capstone/System/)


Embedded Raspberry Pi Program to run on Bellboy devices. Uses _pytest_ and
_mock_ for unit tests, and _pyup.io_ to secure dependencies.


## Usage
```sh
cd bellboy
python main.py [-h]
```
Status:
Starts bellboy services,
runs ultrasonic sensor for event.
(soon) camera stuff

## Development

```sh
# Install dependencies (if on Win10 use admin powershell)
pip install -r requirements/REQUIRMEMENTS.txt

# Activate pre-commit, it'll check your files for mistakes before you commit
pre-commit install
```

To create a new bellboy actor class (that extends generic actor) heres an organization tip:\
Divide the class into
  * state modifying methods (private) and
  * message handling methods (public).

Send any response messages in the message handling methods only.\
Change Actor's status in the private methods Only.\
It will be neat and make testing much easier!

### Submitting Work

When adding new features, please use the semantic commit labels so versioning is accurate:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

## Off-Target Testing

```sh
cd bellboy
python -m pytest tests/

# to enable log prints during testing
python -m pytest -s tests/
```

## Resources

1. [Actor tutorial w/Thespian](https://bytes.yingw787.com/posts/2019/02/02/concurrency_with_python_actor_models/)
2. [Thespian docs](https://thespianpy.com/doc/using.pdf)
3. [Bellboy System Design Docs](https://docs.google.com/document/d/1evlRdKOI3afeYZ6nM9aUaCTM6Om1ZHrmEGwIfv0Pv6I/edit?usp=sharing)
