# Changes


## unreleased

Fixed bug where py3.14 compatibility code had unwanted print calls.


## [4.0.0]

- Drop py3.8 compat
- Remove dependency on `attrs`


### Backwards incompatibility

- Deriving from model classes in `pyclts.models` will not work as before, because these have been
  refactored into dataclasses and are no longer "attrs-decorated".
