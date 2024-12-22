"""Example of using st.grid."""

import numpy as np

import streamlit as st

# Basic 2x2 grid
st.header("Basic 2x2 grid")
cells = st.grid(2)
cells[0].write("Top left")
cells[1].write("Top right")
cells[2].write("Bottom left")
cells[3].write("Bottom right")

# Grid with custom dimensions
st.header("3x2 grid")
cells = st.grid((3, 2))
for i, cell in enumerate(cells):
    cell.write(f"Cell {i+1}")

# Grid with custom column widths
st.header("Custom column widths")
left, middle, right = st.grid([2, 1, 1])
left.write("Wide column")
middle.write("Narrow column")
right.write("Narrow column")

# Grid with styling options
st.header("Styled grid")
with st.expander("Grid with medium gap and borders", expanded=True):
    cells = st.grid(2, gap="medium", border=True)
    cells[0].metric("Temperature", "72°F", "2%")
    cells[1].metric("Humidity", "45%", "-5%")
    cells[2].button("Button 1", use_container_width=True)
    cells[3].button("Button 2", use_container_width=True)

# Grid with vertical alignment
st.header("Vertical alignment")
with st.expander("Grid with different content heights", expanded=True):
    cells = st.grid(2, vertical_alignment="center", border=True)
    cells[0].write("Short content")
    cells[1].write("Longer content that\ntakes up\nmultiple lines")
    cells[2].text_input("Input 1")
    cells[3].text_input("Input 2")

# Grid with images
st.header("Image grid")
with st.expander("3x3 image grid", expanded=True):
    # Create a sample image
    img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

    cells = st.grid(3, gap="small")
    for cell in cells:
        cell.image(img, use_container_width=True)

# Grid with charts
st.header("Chart grid")
with st.expander("2x2 chart grid", expanded=True):
    cells = st.grid([2, 2], gap="medium", border=True)

    # Sample data
    chart_data = np.random.randn(20, 3)

    cells[0].line_chart(chart_data)
    cells[1].bar_chart(chart_data)
    cells[2].area_chart(chart_data)
    cells[3].scatter_chart(chart_data)
