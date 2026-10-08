# Security Policy

## Project Scope

0xF77 is an experimental software and computing research project exploring the computational behavior of Fortran FORMAT descriptions, record-based execution, and mutable program representations.

The repository contains research prototypes, execution harnesses, experimental applications, and supporting evidence. These components are provided for research, reproducibility, and exploration. They are not security-hardened production systems.

## Supported Versions

Security maintenance is currently focused on the latest code on the `main` branch.

Older commits, experimental branches, research specimens, and historical artifacts are preserved for reproducibility but are not guaranteed to receive security fixes.

## Reporting a Vulnerability

Please **do not publicly disclose exploitable vulnerabilities before maintainers have had a reasonable opportunity to investigate**.

Preferred reporting method: GitHub's private vulnerability reporting feature, if enabled, through the repository's Security tab.

If private vulnerability reporting is unavailable, open a public issue requesting a private reporting channel without including exploit details, credentials, or sensitive information.

Include, where possible:

- A concise description of the vulnerability.
- Affected files, components, and versions.
- Steps to reproduce the issue.
- Expected and observed behavior.
- Potential impact.
- Relevant environment and compiler/runtime information.

Please avoid submitting sensitive data or weaponized demonstrations.

## Experimental Execution Risks

Some experiments involve dynamically constructed FORMAT descriptions, mutable records, native compilation, filesystem writes, persistent state, and locally hosted interfaces.

Users should:

- Run unfamiliar experiments in isolated environments.
- Review code and execution scripts before running them.
- Keep backups of persistent experiment data.
- Avoid exposing experimental local servers directly to untrusted networks.
- Treat externally supplied records, FORMAT descriptions, and saved worlds as untrusted input.
- Avoid running experiments with unnecessary system privileges.

The repository does not claim that its experimental mechanisms provide secure isolation or protection against malicious input.

## Disclosure and Remediation

Maintainers will evaluate reports based on reproducibility, potential impact, and available resources.

Validated vulnerabilities may be addressed through code changes, documentation updates, mitigation guidance, or explicit statements of unsupported behavior.

No fixed response or remediation timeline is guaranteed.

## Scope Boundaries

Security reporting should concern the code, artifacts, and interfaces contained in this repository.

Vulnerabilities in unrelated projects or third-party software should be reported to their respective maintainers unless a specific integration within 0xF77 creates the issue.
