from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Sequence, cast

from typing_extensions import Self

from streamlit.delta_generator import DeltaGenerator
from streamlit.proto.Block_pb2 import Block as BlockProto

if TYPE_CHECKING:
    from types import TracebackType

    from streamlit.cursor import Cursor


class GridContainer(DeltaGenerator):
    """A container that lays out its children in a grid."""

    @staticmethod
    def _create(
        parent: DeltaGenerator,
        spec: int | Sequence[int | float],
        gap: Literal["small", "medium", "large"] = "small",
        vertical_alignment: Literal["top", "center", "bottom"] = "top",
        border: bool = False,
    ) -> GridContainer:
        """Create a new instance of GridContainer."""
        # Create grid container
        grid_proto = BlockProto()
        grid = grid_proto.grid
        grid.columns = len(spec) if isinstance(spec, (list, tuple)) else int(spec)
        grid.gap = gap
        grid.vertical_alignment = {
            "top": BlockProto.Column.VerticalAlignment.TOP,
            "center": BlockProto.Column.VerticalAlignment.CENTER,
            "bottom": BlockProto.Column.VerticalAlignment.BOTTOM,
        }[vertical_alignment.lower()]
        grid.show_border = border
        grid_proto.allow_empty = True

        # Get delta path from parent
        delta_path: list[int] = (
            parent._active_dg._cursor.delta_path if parent._active_dg._cursor else []
        )

        # Create grid container
        grid_container = cast(
            GridContainer,
            parent._block(block_proto=grid_proto, dg_type=GridContainer),
        )

        # Store initial configuration
        grid_container._delta_path = delta_path
        grid_container._current_proto = grid_proto
        grid_container._spec = spec
        grid_container._current_cell = 0

        return grid_container

    def __init__(
        self,
        root_container: int | None,
        cursor: Cursor | None,
        parent: DeltaGenerator | None,
        block_type: str | None,
    ):
        """Initialize the GridContainer."""
        super().__init__(root_container, cursor, parent, block_type)

        # Initialized in _create():
        self._current_proto: BlockProto | None = None
        self._delta_path: list[int] | None = None
        self._spec: int | Sequence[int | float] | None = None
        self._current_cell = 0

    def _create_cell(self) -> DeltaGenerator:
        """Create a new grid cell and return it."""
        assert self._current_proto is not None, "Grid not correctly initialized!"
        assert self._spec is not None, "Grid not correctly initialized!"

        # Create cell proto
        cell_proto = BlockProto()
        cell = cell_proto.grid_cell

        # Calculate cell position
        if isinstance(self._spec, list):
            total_weight = sum(float(w) for w in self._spec)
            cell.weight = (
                float(self._spec[self._current_cell % len(self._spec)]) / total_weight
            )
            num_cols = len(self._spec)
        else:
            cell.weight = 1.0 / self._spec
            num_cols = self._spec

        cell.column = self._current_cell % num_cols
        cell.row = self._current_cell // num_cols
        cell.gap = self._current_proto.grid.gap
        cell.vertical_alignment = self._current_proto.grid.vertical_alignment
        cell.show_border = self._current_proto.grid.show_border
        cell_proto.allow_empty = True

        # Increment cell counter
        self._current_cell += 1

        return self._block(cell_proto)

    def __enter__(self) -> Self:  # type: ignore[override]
        # This is a little dubious: we're returning a different type than
        # our superclass' `__enter__` function. Maybe DeltaGenerator.__enter__
        # should always return `self`?
        super().__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Exit the context manager."""
        return super().__exit__(exc_type, exc_val, exc_tb)

    def __getattr__(self, name: str) -> DeltaGenerator:
        """Forward any unknown attribute access to a new grid cell."""
        cell = self._create_cell()
        return getattr(cell, name)
