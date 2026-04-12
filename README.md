# ryl-pre-commit

A [pre-commit](https://pre-commit.com/) hook for
[ryl](https://github.com/owenlamont/ryl), the fast YAML linter written in Rust.

Distributed as a standalone repository so that `ryl` releases published to
[PyPI](https://pypi.org/project/ryl/) can be consumed directly by pre-commit.

## Usage

Add the hook to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/owenlamont/ryl-pre-commit
    # Match the latest ryl release tag.
    rev: v0.6.0
    hooks:
      - id: ryl
```

Pass additional CLI options through the `args` key, for example to point at a
custom configuration file:

```yaml
  - repo: https://github.com/owenlamont/ryl-pre-commit
    rev: v0.6.0
    hooks:
      - id: ryl
        args: [--config-file, configs/yl.yml]
```

## License

MIT (see [LICENSE](LICENSE))
