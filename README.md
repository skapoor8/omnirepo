# Omnirepo

A monorepo management plugin for poetry, inspired by poetry polylith

## Features

### Create a monorepo

```bash
omnirepo init
```

### Add apps and libs

```bash
omnirepo create app --name my_app
omnirepo create lib --name my_lib
```

### Test, Lint, Typecheck and more...

### Run, build and publish

### Templates FTW

### Auto-sync imports

### Run scripts located anywhere in your monorepo

## Development

### Local Installation

```bash
pipx install "$(pwd)"
pipx upgrade omnirepo
pipx uninstall omnirepo
```

## TODO

- [x] local development
- [x] initialize monorepo/workspace
- [x] add libs
- [x] build script
- [x] add apps
- [x] run script
- [ ] sync imports for buildable packages (Error in running quantum rn)
- [ ] dep graph
- [ ] ~~make scripts revertible~~
- [ ] linting - TEST
- [ ] type checking - TEST
- [ ] tests - TEST
- [ ] add cool graphic for omnirepo logo
- [ ] ~~plugin system??? (nope, better off trying to write something with nx maybe? Is it feasable?)~~
- [ ] turn intp poetry plugin
- [ ] publish to pypi
- [ ] make sure templates are included in build

Confusion about:

- [ ] wrapping dir for modules

WISHLIST:

- dependency graph
