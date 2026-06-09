# Changes


## [4.0.2]

- Fixed bug where py3.14 compatibility code had unwanted print calls.
- Fixed bug where the correct css code for the IPA consonant chart was not
  added.


## [4.0.0]

- Drop py3.8 compat
- Remove dependency on `attrs`


### Backwards incompatibility

- Deriving from model classes in `pyclts.models` will not work as before, because these have been
  refactored into dataclasses and are no longer "attrs-decorated".
