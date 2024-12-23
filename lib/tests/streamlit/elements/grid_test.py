"""Unit tests for st.grid."""

import pytest

from streamlit.elements.lib.grid_container import GridContainer
from streamlit.errors import StreamlitAPIException
from streamlit.proto.Block_pb2 import Block as BlockProto
from tests.delta_generator_test_case import DeltaGeneratorTestCase


class GridTest(DeltaGeneratorTestCase):
    """Test ability to create grid layouts."""

    def test_invalid_spec(self):
        """Test that invalid grid specs raise exceptions."""
        with pytest.raises(StreamlitAPIException) as exc_info:
            self.dg.grid("not a number")
        assert "Grid spec must be an int or a list of column weights" in str(
            exc_info.value
        )

        with pytest.raises(StreamlitAPIException) as exc_info:
            self.dg.grid(0)
        assert "Grid columns must be a positive integer" in str(exc_info.value)

        with pytest.raises(StreamlitAPIException) as exc_info:
            self.dg.grid([])
        assert "Grid spec must not be empty" in str(exc_info.value)

        with pytest.raises(StreamlitAPIException) as exc_info:
            self.dg.grid([0, 1, 2])
        assert "Grid column weights must be positive numbers" in str(exc_info.value)

    def test_equal_width_columns(self):
        """Test grid with equal width columns."""
        grid = self.dg.grid(3)
        assert isinstance(grid, GridContainer)

        proto = self._get_last_proto()
        assert proto.grid.columns == 3
        assert proto.grid.gap == "small"
        assert proto.grid.vertical_alignment == BlockProto.Column.VerticalAlignment.TOP
        assert not proto.grid.show_border

    def test_custom_column_widths(self):
        """Test grid with custom column widths."""
        grid = self.dg.grid([2, 1, 1])
        assert isinstance(grid, GridContainer)

        proto = self._get_last_proto()
        assert proto.grid.columns == 3
        assert proto.grid.gap == "small"
        assert proto.grid.vertical_alignment == BlockProto.Column.VerticalAlignment.TOP
        assert not proto.grid.show_border

    def test_styling_options(self):
        """Test grid with styling options."""
        grid = self.dg.grid(2, gap="medium", vertical_alignment="center", border=True)
        assert isinstance(grid, GridContainer)

        proto = self._get_last_proto()
        assert proto.grid.columns == 2
        assert proto.grid.gap == "medium"
        assert (
            proto.grid.vertical_alignment == BlockProto.Column.VerticalAlignment.CENTER
        )
        assert proto.grid.show_border

    def test_grid_cell_creation(self):
        """Test that grid cells are created correctly."""
        grid = self.dg.grid(2)

        # Create first cell
        cell1 = grid._create_cell()
        proto1 = self._get_last_proto()
        assert proto1.grid_cell.column == 0
        assert proto1.grid_cell.row == 0
        assert proto1.grid_cell.weight == 0.5

        # Create second cell
        cell2 = grid._create_cell()
        proto2 = self._get_last_proto()
        assert proto2.grid_cell.column == 1
        assert proto2.grid_cell.row == 0
        assert proto2.grid_cell.weight == 0.5

        # Create third cell (new row)
        cell3 = grid._create_cell()
        proto3 = self._get_last_proto()
        assert proto3.grid_cell.column == 0
        assert proto3.grid_cell.row == 1
        assert proto3.grid_cell.weight == 0.5

    def test_grid_cell_weights(self):
        """Test that grid cells have correct weights with custom column widths."""
        grid = self.dg.grid([2, 1, 1])

        # Create cells
        cell1 = grid._create_cell()
        proto1 = self._get_last_proto()
        assert proto1.grid_cell.weight == 0.5  # 2/4

        cell2 = grid._create_cell()
        proto2 = self._get_last_proto()
        assert proto2.grid_cell.weight == 0.25  # 1/4

        cell3 = grid._create_cell()
        proto3 = self._get_last_proto()
        assert proto3.grid_cell.weight == 0.25  # 1/4

        # Next row should repeat the same weights
        cell4 = grid._create_cell()
        proto4 = self._get_last_proto()
        assert proto4.grid_cell.weight == 0.5

    def test_context_manager(self):
        """Test that grid works as a context manager."""
        with self.dg.grid(2) as grid:
            grid.write("Cell 1")
            grid.write("Cell 2")
            grid.write("Cell 3")

        # Should have created 3 cells
        protos = self._get_all_protos()
        assert len(protos) == 4  # grid + 3 cells

        # Check grid proto
        grid_proto = protos[0]
        assert grid_proto.grid.columns == 2

        # Check cell protos
        for i, proto in enumerate(protos[1:]):
            assert proto.grid_cell.column == i % 2
            assert proto.grid_cell.row == i // 2
            assert proto.grid_cell.weight == 0.5

    def test_method_chaining(self):
        """Test that grid supports method chaining."""
        grid = self.dg.grid(2)
        grid.write("Cell 1").write("Cell 2").write("Cell 3")

        # Should have created 3 cells
        protos = self._get_all_protos()
        assert len(protos) == 4  # grid + 3 cells

        # Check grid proto
        grid_proto = protos[0]
        assert grid_proto.grid.columns == 2

        # Check cell protos
        for i, proto in enumerate(protos[1:]):
            assert proto.grid_cell.column == i % 2
            assert proto.grid_cell.row == i // 2
            assert proto.grid_cell.weight == 0.5
