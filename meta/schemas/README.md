# Schemas

This directory contains the JSON schemas for the TOML files in the `members/`
and `teams/` directories.

## Documentation

See the [schemas documentation directory](../../docs/schemas/) for more information.

## Troubleshooting

If you are using the VSCode extension [tamasfe.even-better-toml](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml), you most likely need to clear the cache to see the changes after updating a schema.

Run the following command to find the cache directory:

```zsh
find ~ -type d -name "tamasfe.even-better-toml"
```

After you delete the cache directory and reload VSCode (or restart the extension),
the extension should start using the updated schemas.
