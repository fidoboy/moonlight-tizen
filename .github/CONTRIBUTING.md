# Contributing

Thank you for contributing to the independently maintained Moonlight Tizen project. Contributions may include bug fixes, Dolby optical-audio compatibility reports, interface improvements, localization, documentation and build automation.

## Before submitting changes

- Check the current code and documentation to avoid duplicate work.
- Keep each pull request focused and explain the user-visible effect.
- Test the changes locally whenever possible, and include the TV model, Tizen version, host software/version and relevant settings when reporting hardware-dependent behavior.
- For Dolby passthrough changes, specify the negotiated codec, channel layout, whether OPUS fallback was tested, and the TV/receiver optical connection used. Do not include passwords, pairing PINs, private keys or unnecessary public IP addresses in logs.
- Update the local documentation when user-facing behavior changes.

## Build and test

Follow the repository's [Development Guide](../docs/Development-Guide.md) for Docker builds, CI artifacts, and versioned public releases. Pull requests should pass the **Build WGT (CI)** workflow.

## Code and dependencies

Follow the existing project structure and style, preserve copyright and license notices, and avoid unrelated formatting or refactoring. Prefer official upstream updates for third-party dependencies where practical. Project-specific modifications to shared dependencies are permitted when needed for this project's functionality; explain the reason and scope in the pull request, and retain the dependency's license requirements.

## Localization

Use `wasm/static/locales/en-US.json` as the source language. Keep locale keys and format placeholders unchanged, translate values only, and check key parity with the other supported locale files.

## Pull requests

Report bugs and request features through the repository's [GitHub Issues](https://github.com/fidoboy/moonlight-tizen-ac3/issues/new/choose). Contributions to the code can be proposed with a pull request against `master`. Describe what changed, how it was tested, known limitations, and any implications for existing OPUS-only hosts. Existing hosts that only provide OPUS must remain supported unless a documented breaking change is explicitly intended.
