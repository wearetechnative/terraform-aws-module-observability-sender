# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Types of changes

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

## [Unreleased]

## [0.0.9]

### Added

- Added Eventbridge rule to notify RDS operational and scheduled changes in AWS healthdashboard.

## [0.0.8]
### Changed

- Updated depricated eventbridge rule ``is_enabled`` argument to ``state``.

## [0.0.7]

### Changed

- Changed /dev device name to correct value.

## [0.0.6]
### Changed

- Added Lambda subscription to observability sns topic in sns module.

## [0.0.5]

### Added

- Module automatically creates an sns topic instead of requesting an sns topic.

### Removed

- The ability to pass an SNS topic arn via a variable.

## [0.0.4]

### Added

- Added default eventbridge rules with the ability to override.

### Changed

- Changed SQS configuration variable.
- Changed eventbridge rules configuration.
- Updated Lambda alarm creator with new changes.

## [0.0.3]

### Added

- ARN and name of Lambda functions as output variables.

### Fixed

- AWS region throwing an error when trying to set it up manually.
- Extended IAM role naming to prevent collisions when deploying in the same account but in different region.

## [0.0.2]

### Updated

- Updated pre-commit to conduct terraform linting.

### Added

- Lambda to forward payload to the monitoring account.

### Fixed

- fixed an issue where Lambda alarm creator would fail due to timeout.
- Missing lambda arguments.
- incorrect locals block declaration.

## [0.0.1]

### Added

- Lift and Shift import of the observability module which was part of the TechNative aws-module repository.
