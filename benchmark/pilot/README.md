# Pilot Benchmark Clusters

This directory contains three pilot clusters that cover:

- public humiliation / dignity-preserving correction
- offer negotiation under social and ethical pressure
- group escalation under partial observability and reputation risk

Each cluster includes a base scene, latent-state notes, and a small set of task items.

## Conventions

- `*_BASE` items define the primary evaluation target for a cluster.
- `*_VARIANT_*` items change one important variable while preserving the rest of the scene.
- Every item in a pilot cluster should have a corresponding entry in `labels/pilot_gold_labels.yaml`.
- Gold labels in the pilot phase should record the minimum required elements for a response to count as correct, not just broad themes.
