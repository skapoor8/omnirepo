# Omnirepo

A monorepo management plugin for poetry

Confusion about:
[ ] wrapping dir for modules
[ ]

TODO:
[x] local development
[x] initialize monorepo/workspace
[x] add libs
[x] build script
[x] add apps
[x] run script
[ ]
[ ] sync imports for buildable packages (Error in running quantum rn)
~~[ ] make scripts revertible~~
[ ] linting - TEST
[ ] type checking - TEST
[ ] tests - TEST
~~[ ] plugin system??? (nope, better off trying to write something with nx maybe? Is it feasable?)~~
[ ] turn intp poetry plugin
[ ] publish to pypi
[ ] make sure templates are included in build

WISHLIST:

- dependency graph
-

## Development

### Local Installation

```bash
pipx install "$(pwd)"
pipx upgrade omnirepo
pipx uninstall omnirepo
```
