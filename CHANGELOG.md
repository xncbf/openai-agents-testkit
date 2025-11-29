# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-XX-XX

### Added

- Initial release
- `FakeModel` class for testing without API calls
- `FakeModelProvider` for managing fake model instances
- pytest fixtures: `fake_model`, `fake_model_provider`, `fake_model_provider_factory`, `no_delay_provider`
- Call tracking with `call_count` and `call_history`
- Custom response factory support
