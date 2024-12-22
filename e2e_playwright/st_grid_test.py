"""Test st.grid."""

from playwright.sync_api import Page, expect

from e2e_playwright.conftest import ImageCompareFunction


def test_basic_grid_layout(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that basic 2x2 grid is rendered correctly."""
    grid = app.get_by_test_id("stGrid").first
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-basic_2x2")


def test_custom_dimensions(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid with custom dimensions (3x2)."""
    grid = app.get_by_test_id("stGrid").nth(1)
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-3x2")


def test_custom_column_widths(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid with custom column widths."""
    grid = app.get_by_test_id("stGrid").nth(2)
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-custom_widths")


def test_styled_grid(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid with styling options (gap and border)."""
    expander = app.get_by_text("Grid with medium gap and borders")
    expander.click()
    grid = app.get_by_test_id("stGrid").nth(3)
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-styled")


def test_vertical_alignment(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid with different vertical alignments."""
    expander = app.get_by_text("Grid with different content heights")
    expander.click()
    grid = app.get_by_test_id("stGrid").nth(4)
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-vertical_alignment")


def test_image_grid(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid with images."""
    expander = app.get_by_text("3x3 image grid")
    expander.click()
    grid = app.get_by_test_id("stGrid").nth(5)
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-images")


def test_chart_grid(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid with different chart types."""
    expander = app.get_by_text("2x2 chart grid")
    expander.click()
    grid = app.get_by_test_id("stGrid").nth(6)
    expect(grid).to_be_visible()
    assert_snapshot(grid, name="st_grid-charts")


def test_grid_responsiveness(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid responsiveness at different viewport widths."""
    # Test at wide viewport
    app.set_viewport_size({"width": 1200, "height": 800})
    grid = app.get_by_test_id("stGrid").first
    assert_snapshot(grid, name="st_grid-responsive_wide")

    # Test at medium viewport
    app.set_viewport_size({"width": 800, "height": 800})
    assert_snapshot(grid, name="st_grid-responsive_medium")

    # Test at narrow viewport
    app.set_viewport_size({"width": 400, "height": 800})
    assert_snapshot(grid, name="st_grid-responsive_narrow")


def test_grid_in_sidebar(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid behavior when placed in sidebar."""
    # Find the sidebar grid
    sidebar = app.get_by_text("Sidebar grid example:")
    expect(sidebar).to_be_visible()

    # Get the grid within the sidebar
    grid = app.locator(".stSidebar").get_by_test_id("stGrid").first
    expect(grid).to_be_visible()

    # Test at different viewport widths
    app.set_viewport_size({"width": 1200, "height": 800})
    assert_snapshot(grid, name="st_grid-sidebar_wide")

    app.set_viewport_size({"width": 800, "height": 800})
    assert_snapshot(grid, name="st_grid-sidebar_medium")

    app.set_viewport_size({"width": 400, "height": 800})
    assert_snapshot(grid, name="st_grid-sidebar_narrow")


def test_grid_in_columns(app: Page, assert_snapshot: ImageCompareFunction):
    """Test grid behavior when placed inside columns."""
    # Find the column grids
    left_grid = app.get_by_text("Left column grid:").get_by_test_id("stGrid").first
    right_grid = app.get_by_text("Right column grid:").get_by_test_id("stGrid").first

    expect(left_grid).to_be_visible()
    expect(right_grid).to_be_visible()

    # Test at different viewport widths
    app.set_viewport_size({"width": 1200, "height": 800})
    assert_snapshot(left_grid, name="st_grid-column_left_wide")
    assert_snapshot(right_grid, name="st_grid-column_right_wide")

    app.set_viewport_size({"width": 800, "height": 800})
    assert_snapshot(left_grid, name="st_grid-column_left_medium")
    assert_snapshot(right_grid, name="st_grid-column_right_medium")

    app.set_viewport_size({"width": 400, "height": 800})
    assert_snapshot(left_grid, name="st_grid-column_left_narrow")
    assert_snapshot(right_grid, name="st_grid-column_right_narrow")
