import streamlit as st
from bs4 import BeautifulSoup
import json

def parse_bead_road_svg(svg_code):
    soup = BeautifulSoup(svg_code, 'html.parser')
    
    # Initialize 6x15 grid with empty strings
    grid = [['' for _ in range(15)] for _ in range(6)]
    
    # Find all coordinate elements
    coordinates = soup.find_all('svg', attrs={'data-type': 'coordinates'})
    
    for coord in coordinates:
        # Get x, y coordinates
        x = int(float(coord.get('data-x', 0)))
        y = int(float(coord.get('data-y', 0)))
        
        # Find the result text (B, P, or T)
        text_elem = coord.find('text')
        if text_elem and text_elem.string:
            result = text_elem.string.strip()
            if 0 <= y < 6 and 0 <= x < 15:  # Ensure within grid bounds
                grid[y][x] = result.lower()
    
    return grid

def display_grid(grid):
    # CSS for the grid
    st.markdown("""
        <style>
        .grid-container {
            display: table;
            border-collapse: collapse;
            margin: 20px 0;
            overflow-x: auto;
        }
        .grid-row {
            display: table-row;
        }
        .bead-road-cell {
            width: 40px;
            height: 40px;
            border: 1px solid black;
            display: table-cell;
            text-align: center;
            vertical-align: middle;
            font-family: monospace;
            font-size: 16px;
            position: relative;
        }
        .banker { color: red; font-weight: bold; }
        .player { color: blue; font-weight: bold; }
        .tie { color: green; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    # Display the grid with container
    html_table = ['<div class="grid-container" style="max-width: 100%; overflow-x: auto;">']
    for y, row in enumerate(grid):
        html_table.append('<div class="grid-row">')
        for x, cell in enumerate(row[:15]):
            css_class = ''
            if cell == 'b':
                css_class = 'banker'
            elif cell == 'p':
                css_class = 'player'
            elif cell == 't':
                css_class = 'tie'
            html_table.append(f'<div class="bead-road-cell {css_class}">{cell.upper() if cell else "&nbsp;"}</div>')
        html_table.append('</div>')
    html_table.append('</div>')
    
    st.markdown(''.join(html_table), unsafe_allow_html=True)

def divide_grid_into_overlapping_zones(grid, zone_width=3):
    """
    Divide the grid into overlapping zones based on the specified zone width.
    """
    zones = []
    num_cols = len(grid[0])  # Total number of columns in the grid
    
    for start_col in range(num_cols - zone_width + 1):
        end_col = start_col + zone_width
        zone_data = [row[start_col:end_col] for row in grid]
        
        # Check if the zone contains any 'b', 't', or 'p'
        contains_data = any(cell in {'b', 't', 'p'} for row in zone_data for cell in row)
        
        if contains_data:  # Only include zones with relevant data
            zones.append({
                'zone_data': zone_data,
                'start_col': start_col,
                'end_col': end_col - 1
            })
    
    return zones

def display_zones(zones):
    """
    Display the divided zones on the Streamlit interface.
    """
    for idx, zone in enumerate(zones):
        st.markdown(f"### Zone {idx + 1} (Columns {zone['start_col'] + 1} to {zone['end_col'] + 1})")
        
        # CSS for the zone grid
        st.markdown("""
            <style>
            .zone-container {
                display: table;
                border-collapse: collapse;
                margin: 10px 0;
                overflow-x: auto;
            }
            .zone-row {
                display: table-row;
            }
            .zone-cell {
                width: 40px;
                height: 40px;
                border: 1px solid black;
                display: table-cell;
                text-align: center;
                vertical-align: middle;
                font-family: monospace;
                font-size: 16px;
            }
            .banker { color: red; font-weight: bold; }
            .player { color: blue; font-weight: bold; }
            .tie { color: green; font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)
        
        # Render the zone grid
        html_zone = ['<div class="zone-container">']
        for row in zone['zone_data']:
            html_zone.append('<div class="zone-row">')
            for cell in row:
                css_class = ''
                if cell == 'b':
                    css_class = 'banker'
                elif cell == 'p':
                    css_class = 'player'
                elif cell == 't':
                    css_class = 'tie'
                html_zone.append(
                    f'<div class="zone-cell {css_class}">'
                    f'{cell.upper() if cell else "&nbsp;"}'
                    f'</div>'
                )
            html_zone.append('</div>')
        html_zone.append('</div>')
        
        st.markdown(''.join(html_zone), unsafe_allow_html=True)

def main():
    st.title("Bead Road Parser")
    
    # Initialize session state for text area
    if 'reset_clicked' not in st.session_state:
        st.session_state.reset_clicked = False
    
    # Text area for SVG input
    if st.session_state.reset_clicked:
        svg_code = st.text_area("Paste SVG code here", value="", height=200, key='svg_input')
        st.session_state.reset_clicked = False
    else:
        svg_code = st.text_area("Paste SVG code here", height=200, key='svg_input')
    
    # Create columns for buttons
    col1, col2 = st.columns([1, 4])
    
    # Buttons in columns
    with col1:
        if st.button("Reset"):
            st.session_state.reset_clicked = True
            st.experimental_rerun()
    
    with col2:
        if st.button("Parse SVG"):
            if svg_code:
                try:
                    # Step 1: Parse the SVG code into a grid
                    grid = parse_bead_road_svg(svg_code)
                    st.success("Successfully parsed the SVG code!")
                    
                    # Step 2: Display the full grid
                    st.subheader("Full Grid")
                    display_grid(grid)
                    
                    # Step 3: Divide the grid into overlapping zones (3 columns per zone)
                    zones = divide_grid_into_overlapping_zones(grid, zone_width=3)
                    
                    # Step 4: Display the divided zones
                    if zones:
                        st.subheader("Divided Zones")
                        display_zones(zones)
                    else:
                        st.info("No zones with relevant data to display.")
                    
                except Exception as e:
                    st.error(f"Error parsing SVG: {str(e)}")
            else:
                st.warning("Please paste SVG code first")

if __name__ == "__main__":
    main()