# ryl-pre-commit

A [pre-commit](https://pre-commit.com/) hook for
[ryl](https://github.com/owenlamont/ryl), the fast YAML linter and formatter.

Distributed as a standalone repository so that `ryl` releases published to
[PyPI](https://pypi.org/project/ryl/) can be consumed directly by pre-commit.

## Usage

Add the hooks to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/owenlamont/ryl-pre-commit
    # Match the latest ryl release tag.
    rev: v0.25.1
    hooks:
      # Run the linter.
      - id: ryl-check
      # Run the formatter.
      - id: ryl-format
```

To apply safe fixes, pass `--fix` to `ryl-check` and list it before
`ryl-format`, since a fix can leave layout the formatter then changes:

```yaml
      - id: ryl-check
        args: [--fix]
      - id: ryl-format
```

Pass other CLI options through `args`, for example a custom configuration file:

```yaml
      - id: ryl-check
        args: [--config-file, configs/ryl.toml]
```

The `ryl` id still runs `ryl check`, as a legacy alias for `ryl-check`.

## YAML embedded in Markdown

`ryl-check-markdown` and `ryl-format-markdown` lint and format front matter and
fenced `yaml`/`yml` blocks in `.md`, `.markdown`, `.mdx`, `.qmd` and `.Rmd`
files, with no extra `[files]` config:

```yaml
  - repo: https://github.com/owenlamont/ryl-pre-commit
    rev: v0.25.1
    hooks:
      - id: ryl-check-markdown
      - id: ryl-format-markdown
```

`ryl-markdown` remains as a legacy alias for `ryl-check-markdown`. The format
hooks need `ryl >= 0.25.0`.

## License

MIT (see [LICENSE](LICENSE))
