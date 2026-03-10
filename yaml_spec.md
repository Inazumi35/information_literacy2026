# YAML Lecture Format Specification

## Overview

Claude (Web) generates YAML files, Claude Code converts them to Beamer .tex files.

## YAML Structure

```yaml
num: "01"                    # Lecture number (zero-padded)
title: "Lecture Title"       # Main title
subtitle: "Sub info"         # Optional subtitle
textbook: "p.4-9"           # Textbook pages (or "-")
next_topic: "Next Title"     # Next lecture topic
next_pages: "p.10-19"       # Next lecture pages (or "-")

slides:
  - type: <slide_type>
    ...
```

## Slide Types

### 1. `title` - Title + Today's Flow

```yaml
- type: title
  flow:
    - "Step 1"
    - "Step 2"
    - "Step 3"
```

### 2. `terms` - Terminology Definitions

```yaml
- type: terms
  title: "Key Terms"         # Optional (default: "Key Terms")
  items:
    - term: "LMS"
      desc: "Learning Management System"
    - term: "e-Learning"
      desc: "Online learning via internet"
```

### 3. `points` - Key Points

```yaml
- type: points
  title: "Important Points"  # Optional
  items:
    - "Point 1"
    - "Point 2"
  supplement:                # Optional
    - "Extra info 1"
    - "Extra info 2"
```

### 4. `code` - Code Example (adds [fragile])

```yaml
- type: code
  title: "Python Example"
  language: "Python"
  label: "Hello World"       # Block label
  code: |
    def hello():
        print("Hello!")
    hello()
```

### 5. `practice` - Hands-on Practice

```yaml
- type: practice
  title: "Hands-on"          # Optional
  desc: "Follow the steps."  # Optional instruction
  steps:
    - "Step 1"
    - "Step 2"
    - "Step 3"
```

### 6. `notice` - Notices + Supplement

```yaml
- type: notice
  title: "Common Mistakes"   # Optional
  items:
    - "Warning 1"
    - "Warning 2"
  supplement:                # Optional
    - "Extra note"
```

### 7. `exercise` - Exercises

```yaml
- type: exercise
  title: "Exercises"         # Optional
  basic:
    - "Problem 1"
    - "Problem 2"
  advanced:                  # Optional
    - "Challenge 1"
```

### 8. `assignment` - Assignment + Next Preview (usually last slide)

```yaml
- type: assignment
  task: "Submit via Teams."
  # next_topic and next_pages auto-filled from metadata
```

### 9. `table` - Table

```yaml
- type: table
  title: "Comparison"
  headers: ["Item", "Value A", "Value B"]
  rows:
    - ["Item 1", "100", "200"]
    - ["Item 2", "300", "400"]
```

### 10. `twocol` - Two-Column Layout

```yaml
- type: twocol
  title: "Comparison"
  left:
    label: "Method A"        # Block title
    items:
      - "Feature 1"
      - "Feature 2"
  right:
    label: "Method B"
    items:
      - "Feature 1"
      - "Feature 2"
```

### 11. `free` - Raw LaTeX

```yaml
- type: free
  title: "Custom Slide"
  fragile: true              # Optional, for lstlisting
  latex: |
    \begin{columns}[T]
      \begin{column}{0.48\textwidth}
        custom content
      \end{column}
    \end{columns}
```

## File Naming

- YAML: `lecture_01.yaml`
- Generated: `lecture_01.tex`

## Example Prompt for Claude (Web)

> "Create lecture_03.yaml for 'Information and Media Characteristics'.
> Use the yaml_spec.md format. Include: title, terms (3 terms),
> points, exercise, and assignment slides."
