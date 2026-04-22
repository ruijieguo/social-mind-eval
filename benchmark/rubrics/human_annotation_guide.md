# Human Annotation Guide

When labeling a cluster:

1. Identify the primary dimension before reviewing candidate answers.
2. Mark which latent-state facts are required for a correct answer.
3. Distinguish descriptive error from normative error.
4. Use the primary question rule:
   - what is this situation -> dimension 1
   - who thinks what -> dimension 2
   - why is this happening -> dimension 3
   - what happens next -> dimension 4
   - what should be done -> dimension 5
   - how should it be said -> dimension 6

## Ambiguity rule

If a prompt touches multiple dimensions, assign the primary dimension based on the main thing the question asks the model to decide, not the scene topic.

- If the prompt asks for a prediction, prefer dimension 4 even if norms are present.
- If the prompt asks for a boundary judgment, prefer dimension 5 even if a response could also be written.
- If the prompt asks for an actual reply, prefer dimension 6.

## Annotation minimum

For each item, record:

1. primary dimension
2. required latent-state facts
3. expected success condition
4. one common failure mode
