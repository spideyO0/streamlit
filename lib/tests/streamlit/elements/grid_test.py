"""Unit tests for st.grid."""

from parameterized import parameterized

from streamlit.errors import StreamlitAPIException
from streamlit.proto.Block_pb2 import Block as BlockProto
from tests.delta_generator_test_case import DeltaGeneratorTestCase


class GridTest(DeltaGeneratorTestCase):
    """Test st.grid."""

    def test_basic_grid(self):
        """Test that basic grid works with integer spec."""
        cells = self.dg.grid(2)  # 2x2 grid

        all_deltas = self.get_all_deltas_from_queue()

        # Should create 1 grid container and 4 cells
        self.assertEqual(len(all_deltas), 5)

        grid_proto = all_deltas[0].add_block
        self.assertEqual(grid_proto.grid.rows, 2)
        self.assertEqual(grid_proto.grid.columns, 2)
        self.assertEqual(grid_proto.grid.gap, "small")
        self.assertEqual(
            grid_proto.grid.vertical_alignment, BlockProto.Column.VerticalAlignment.TOP
        )
        self.assertFalse(grid_proto.grid.show_border)

        # Check cells
        for i, cell in enumerate(all_deltas[1:]):
            cell_proto = cell.add_block.grid_cell
            self.assertEqual(cell_proto.row, i // 2)
            self.assertEqual(cell_proto.column, i % 2)
            self.assertEqual(cell_proto.weight, 0.5)  # 1/2 for equal width
            self.assertEqual(cell_proto.gap, "small")
            self.assertEqual(
                cell_proto.vertical_alignment, BlockProto.Column.VerticalAlignment.TOP
            )
            self.assertFalse(cell_proto.show_border)

    def test_tuple_spec(self):
        """Test grid with tuple spec for rows and columns."""
        cells = self.dg.grid((3, 2))  # 3x2 grid

        all_deltas = self.get_all_deltas_from_queue()

        grid_proto = all_deltas[0].add_block
        self.assertEqual(grid_proto.grid.rows, 3)
        self.assertEqual(grid_proto.grid.columns, 2)

    def test_list_spec(self):
        """Test grid with list spec for custom column widths."""
        cells = self.dg.grid([2, 1, 1])  # Single row, 3 columns with weights

        all_deltas = self.get_all_deltas_from_queue()

        grid_proto = all_deltas[0].add_block
        self.assertEqual(grid_proto.grid.rows, 1)
        self.assertEqual(grid_proto.grid.columns, 3)

        # Check cell weights
        weights = [0.5, 0.25, 0.25]  # Normalized weights
        for i, cell in enumerate(all_deltas[1:]):
            self.assertEqual(cell.add_block.grid_cell.weight, weights[i])

    def test_invalid_spec(self):
        """Test that invalid specs raise appropriate exceptions."""
        with self.assertRaises(StreamlitAPIException):
            self.dg.grid("invalid")

        with self.assertRaises(StreamlitAPIException):
            self.dg.grid(0)  # Zero dimensions

        with self.assertRaises(StreamlitAPIException):
            self.dg.grid(-1)  # Negative dimensions

        with self.assertRaises(StreamlitAPIException):
            self.dg.grid(13)  # Too large (exceeds 144 cells)

    @parameterized.expand(
        [
            ("small", BlockProto.Column.VerticalAlignment.TOP, False),
            ("medium", BlockProto.Column.VerticalAlignment.CENTER, True),
            ("large", BlockProto.Column.VerticalAlignment.BOTTOM, False),
        ]
    )
    def test_grid_options(self, gap, vertical_alignment, border):
        """Test grid with various options."""
        cells = self.dg.grid(
            2,
            gap=gap,
            vertical_alignment=vertical_alignment.name.lower(),
            border=border,
        )

        all_deltas = self.get_all_deltas_from_queue()
        grid_proto = all_deltas[0].add_block

        self.assertEqual(grid_proto.grid.gap, gap)
        self.assertEqual(grid_proto.grid.vertical_alignment, vertical_alignment)
        self.assertEqual(grid_proto.grid.show_border, border)

        # Check that options are propagated to cells
        for cell in all_deltas[1:]:
            cell_proto = cell.add_block.grid_cell
            self.assertEqual(cell_proto.gap, gap)
            self.assertEqual(cell_proto.vertical_alignment, vertical_alignment)
            self.assertEqual(cell_proto.show_border, border)
