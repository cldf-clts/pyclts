# Changes


## [4.0.0] - unreleased

- Drop py3.8 compat
- Remove dependency on `attrs`


### Backwards incompatibility

- Deriving from model classes in `pyclts.models` will not work as before, because these have been
  refactored into dataclasses and are no longer "attrs-decorated".
