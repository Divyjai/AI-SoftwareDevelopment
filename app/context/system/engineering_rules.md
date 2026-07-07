# Engineering Rules & Constitution

## Constitutional Rule 1: The Meaningful Action Contract
Every meaningful action in the system MUST produce three outputs:
1. **Project State Update**: The current truth of the project must be explicitly updated.
2. **Versioned Artifact(s)**: The persistent result of the work must be saved as an artifact.
3. **Event Emission**: The signal that drives the next workflow step must be emitted to the Event Bus.

## Coding Standards
- No hardcoded secrets.
- Full typing in Python.
- Test-driven development is preferred.
