"""Viveka answer engine (prototype).

Runs entirely locally: understanding, retrieval and composition are
deterministic, and nothing is sent to any provider or saved to disk.
See engine/core.py for the pipeline: understand -> clarify -> retrieve ->
compare -> recommend -> challenge -> act.
"""

from .core import answer, load_library  # noqa: F401
