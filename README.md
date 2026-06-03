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
    rev: v0.12.0
    hooks:
      - id: ryl
```

Pass additional CLI options through the `args` key, for example to point at a
custom configuration file:

```yaml
  - repo: https://github.com/owenlamont/ryl-pre-commit
    rev: v0.12.0
    hooks:
      - id: ryl
        args: [--config-file, configs/yl.yml]
```

## Linting YAML embedded in Markdown

The `ryl` hook above only sees YAML files. To also lint YAML embedded in
Markdown — front matter and fenced `yaml`/`yml` blocks — add the `ryl-markdown`
hook, which runs `ryl --markdown` and so needs no extra `[files]` config:

```yaml
  - repo: https://github.com/owenlamont/ryl-pre-commit
    rev: v0.12.0
    hooks:
      - id: ryl
      - id: ryl-markdown
```

It targets `.md`, `.markdown`, `.mdx`, `.qmd`, and `.Rmd` files. To autofix the
embedded YAML in place, add `args: [--fix]`:

```yaml
      - id: ryl-markdown
        args: [--fix]
```

Requires `ryl >= 0.11.0`.

## License

MIT (see [LICENSE](LICENSE))
