# Chunking Strategy

This document details the strategy used for splitting product knowledge documents into manageable chunks for the retrieval system.

## Recursive Character Text Splitting

We use a recursive splitting approach to maintain semantic integrity.

- **Objective**: Ensure that related information stays together and that chunks do not break mid-sentence or mid-paragraph.
- **Paramters**: 
    - `chunk_size`: Typically between 500-1000 characters.
    - `chunk_overlap`: A small percentage (e.g., 10-20%) to provide context across boundaries.

## Handling Special Formats

- **Headers**: Splitting logic prioritizes breaks at header levels (e.g., `###`).
- **Lists**: Bullet points are kept within the same chunk whenever possible.
