"""Example of using st.grid."""

import numpy as np

import streamlit as st

# Basic 2x2 grid
st.header("Basic 2x2 grid")
with st.grid(2) as grid:
    grid.write("Top left")
    grid.write("Top right")
    grid.write("Bottom left")
    grid.write("Bottom right")

# Grid with custom dimensions
st.header("3x2 grid")
with st.grid(3) as grid:
    for i in range(6):
        grid.write(f"Cell {i+1}")

# Grid with custom column widths
st.header("Custom column widths")
grid = st.grid([2, 1, 1])
grid.write("Wide column")
grid.write("Narrow column")
grid.write("Narrow column")

# Grid with styling options
st.header("Styled grid")
with st.expander("Grid with medium gap and borders", expanded=True):
    grid = st.grid(2, gap="medium", border=True)
    grid.metric("Temperature", "72°F", "2%")
    grid.metric("Humidity", "45%", "-5%")
    grid.button("Button 1", use_container_width=True)
    grid.button("Button 2", use_container_width=True)

# Grid with vertical alignment
st.header("Vertical alignment")
with st.expander("Grid with different content heights", expanded=True):
    grid = st.grid(2, vertical_alignment="center", border=True)
    grid.write("Short content")
    grid.write("Longer content that\ntakes up\nmultiple lines")
    grid.text_input("Input 1")
    grid.text_input("Input 2")

# Grid with images
st.header("Image grid")
with st.expander("3x3 image grid", expanded=True):
    # Create a sample image
    img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

    grid = st.grid(3, gap="small")
    for _ in range(9):
        grid.image(img, use_container_width=True)

# Grid with charts
st.header("Chart grid")
with st.expander("2x2 chart grid", expanded=True):
    grid = st.grid(2, gap="medium", border=True)

    # Sample data
    chart_data = np.random.randn(20, 3)

    grid.line_chart(chart_data)
    grid.bar_chart(chart_data)
    grid.area_chart(chart_data)
    grid.scatter_chart(chart_data)

# Grid in sidebar
st.header("Grid in sidebar")
with st.sidebar:
    st.write("Sidebar grid example:")
    grid = st.grid(2, gap="small", border=True)
    grid.button("Sidebar Button 1", use_container_width=True)
    grid.button("Sidebar Button 2", use_container_width=True)
    grid.text_input("Sidebar Input 1")
    grid.text_input("Sidebar Input 2")

# Grid in columns
st.header("Grid in columns")
col1, col2 = st.columns(2)

with col1:
    st.write("Left column grid:")
    grid = st.grid(2, gap="small")
    grid.metric("Value 1", "100", "+10")
    grid.metric("Value 2", "200", "-5")
    grid.metric("Value 3", "300", "+15")
    grid.metric("Value 4", "400", "-8")

with col2:
    st.write("Right column grid:")
    grid = st.grid(2, gap="small")
    for i in range(4):
        grid.write(f"Nested cell {i+1}")
