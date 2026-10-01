# Testing

The CI test workflow runs the Python unit tests with the standard library `unittest` runner.

## Test stack

|Tool|Purpose|
|---|---|
|`unittest`|Exercises exporter, relay or sanitizer behavior.|

## Running the tests

Run the same discovery command used by CI from the repository root.

```bash
python -m unittest discover -s tests -v
```

## Test layout

Tests live in the paths selected by that discovery command. Add cases beside the existing suite and follow its fixture and mocking patterns.
