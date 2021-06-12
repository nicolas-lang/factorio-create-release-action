# GitHub Action for Factorio Mod Release

This action will upload the latest release of your mod to the [Factorio Mod Portal](https://mods.factorio.com/)
You need to perform the initial upload to the portal manually to register the mod's metadata.

## Sample Workflow

A sample workflow that uses this action can be found at [nicolas-lang/Factorio.ModTemplate](https://github.com/nicolas-lang/Factorio.ModTemplate)

## Inputs

### `factorio_user`

**Required** User that will be used to authenticate to the Factorio mod-portal.

### `factorio_password`

**Required** Password that will be used to authenticate to the Factorio mod-portal.

## Acknowledgements

Factorio build scripts based on:

- [Roang-zero1](https://github.com/Roang-zero1)
- [Nexelas](https://github.com/Nexela)
- [Shane Madden](https://github.com/shanemadden)
