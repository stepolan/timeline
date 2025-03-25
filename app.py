import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import json
import os
import io

# Set dark theme for Streamlit
st.set_page_config(page_title="Timeline Generator", layout="wide")
st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

def save_timeline(df, filename='timeline_data.json'):
    """Save timeline data to a JSON file"""
    if not df.empty:
        data = {
            'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'milestones': df['milestone'].tolist()
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

def load_timeline(filename='timeline_data.json'):
    """Load timeline data from a JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            df = pd.DataFrame({
                'date': pd.to_datetime(data['dates']),
                'milestone': data['milestones']
            })
            return df
    return pd.DataFrame(columns=['date', 'milestone'])

def format_date(date, granularity):
    if isinstance(date, str):
        date = pd.to_datetime(date)
    
    if granularity == "Date":
        return date.strftime("%d %b %Y")
    elif granularity == "Month":
        return date.strftime("%b %Y")
    elif granularity == "Quarter":
        return f"Q{(date.month-1)//3 + 1} {date.year}"
    else:  # Year
        return str(date.year)

def create_timeline(milestones_df, granularity, alternate_sides=True, 
                   show_lines=True, date_distance=0.10, milestone_distance=0.85,
                   line_length=0.35, dash_density=0.6, dpi=300,
                   milestone_color='#CCCCCC', line_color='#808080',
                   date_color='white', timeline_color='#14823C',
                   circle_color='#808080', background_color='black',
                   show_title=True, title_text="Startup Progress Timeline"):
    if len(milestones_df) == 0:
        return None
        
    # Create the figure and axis with dark background
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6), dpi=dpi)
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    # Sort milestones by date
    milestones_df = milestones_df.sort_values('date')
    
    # Format dates based on granularity
    formatted_dates = [format_date(date, granularity) for date in milestones_df['date']]
    milestones = [str(m).replace('\\n', '\n') for m in milestones_df['milestone'].tolist()]

    # Get current date for future/past comparison
    current_date = pd.Timestamp.now()
    is_future = [date > current_date for date in milestones_df['date']]

    # Constants
    circle_radius = 10/72  # Convert 10 point marker size to axis units

    # Draw timeline segments with appropriate styles
    for i in range(len(milestones)):
        if i < len(milestones) - 1:
            # Draw segment between current and next milestone
            start_x = i
            end_x = i + 1
            if is_future[i] or is_future[i + 1]:
                # If either milestone is in future, use dashed line
                ax.hlines(1, start_x, end_x, linewidth=2, color=timeline_color,
                         linestyles=(0, (2, dash_density)))
            else:
                # Both milestones are past, use solid line
                ax.hlines(1, start_x, end_x, linewidth=2, color=timeline_color)
    
    # Draw first and last segments of timeline
    if len(milestones) > 0:
        # First segment (to first milestone)
        if is_future[0]:
            ax.hlines(1, -0.5, 0, linewidth=2, color=timeline_color,
                     linestyles=(0, (2, dash_density)))
        else:
            ax.hlines(1, -0.5, 0, linewidth=2, color=timeline_color)
        
        # Last segment (after last milestone)
        if is_future[-1]:
            ax.hlines(1, len(milestones)-1, len(milestones)-0.5, linewidth=2, 
                     color=timeline_color, linestyles=(0, (2, dash_density)))
        else:
            ax.hlines(1, len(milestones)-1, len(milestones)-0.5, linewidth=2, 
                     color=timeline_color)

    # Plot milestones with annotations
    for i, (date, milestone, future) in enumerate(zip(formatted_dates, milestones, is_future)):
        # Determine if this milestone should be above or below the line
        milestone_is_above = False if not alternate_sides else (i % 2 == 1)
        # Date always goes on opposite side
        date_is_above = not milestone_is_above
        
        # Calculate base positions
        if milestone_is_above:
            milestone_y = 1 + milestone_distance
            date_y = 1 - date_distance
            line_start = 1 + circle_radius
            line_end = line_start + (milestone_distance * line_length)
        else:
            milestone_y = 1 - milestone_distance
            date_y = 1 + date_distance
            line_start = 1 - circle_radius
            line_end = line_start - (milestone_distance * line_length)
        
        # Draw milestone marker
        if future:
            # Future milestone: open circle
            ax.plot(i, 1, marker='o', markersize=10, markerfacecolor='none', 
                   markeredgewidth=2, color=circle_color)
        else:
            # Past milestone: filled circle
            ax.plot(i, 1, marker='o', markersize=10, color=circle_color)

        # Draw connecting lines if enabled
        if show_lines:
            ax.vlines(i, line_start, line_end, color=line_color, alpha=0.7)

        # Annotate the date
        ax.text(i, date_y, date, ha='center', va='bottom' if date_is_above else 'top',
                fontsize=10, fontweight='bold', color=date_color)

        # Process milestone text with proper line breaks
        lines = milestone.split('\n')
        
        # Add text lines with proper spacing
        line_height = 0.1
        text_block_height = len(lines) * line_height
        
        # Calculate starting y position for text block
        if milestone_is_above:
            text_start_y = milestone_y  # Start from base position and move down
        else:
            text_start_y = milestone_y + text_block_height - line_height  # Start from top of block
        
        # Add text lines with proper spacing (always top to bottom)
        for j, line in enumerate(lines):
            text_y = text_start_y - (j * line_height)  # Always move down
            ax.text(i, text_y, line, ha='center', 
                   va='bottom' if milestone_is_above else 'top',
                   fontsize=8, color=milestone_color)

    # Adjust plot limits and remove axes
    ax.set_xlim(-0.5, len(milestones)-0.5)
    max_distance = max(date_distance, milestone_distance)
    y_margin = max_distance + 0.1 * max(len(m.split('\n')) for m in milestones)
    ax.set_ylim(1 - y_margin - 0.2, 1 + y_margin + 0.2)
    ax.axis('off')
    
    # Only show title if enabled
    if show_title:
        ax.set_title(title_text, fontsize=12, pad=20, color=date_color)
    
    return fig

def main():
    st.title("Timeline Generator")
    st.write("Create your own milestone timeline by adding dates and descriptions.")

    # Initialize session state for storing milestones
    if 'milestones_df' not in st.session_state:
        st.session_state.milestones_df = load_timeline()

    # File upload
    uploaded_file = st.file_uploader("Upload Timeline Data (CSV)", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if 'date' in df.columns and 'milestone' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                st.session_state.milestones_df = df
                save_timeline(df)
                st.success("Data uploaded successfully!")
            else:
                st.error("CSV must contain 'date' and 'milestone' columns")
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
    
    # Create tabs for settings
    tab1, tab2, tab3 = st.tabs(["Timeline Layout", "Visual Style", "Colors"])
    
    with tab1:
        st.markdown("### Basic Layout")
        col1, col2 = st.columns(2)
        with col1:
            alternate_sides = st.toggle("Alternate milestone positions", value=True)
        with col2:
            show_lines = st.toggle("Show connecting lines", value=True)

        st.markdown("### Distance Controls")
        col1, col2 = st.columns(2)
        with col1:
            milestone_distance = st.slider("Description Distance", 0.1, 1.0, 0.85, 0.01,
                                        help="Distance of milestone descriptions from the timeline")
            date_distance = st.slider("Date Distance", 0.1, 1.0, 0.10, 0.01,
                                    help="Distance of dates from the timeline")
        with col2:
            line_length = st.slider("Connecting Line Length", 0.1, 1.0, 0.35, 0.05,
                                  help="How far the connecting lines extend (as a fraction of the milestone distance)")
            
    with tab2:
        st.markdown("### Timeline Style")
        col1, col2 = st.columns(2)
        with col1:
            dash_density = st.slider("Future Timeline Dash Density", 0.5, 5.0, 0.6, 0.1,
                                   help="Controls the density of dashes in future timeline segments")
        with col2:
            dpi = st.slider("Image Quality (DPI)", 100, 1200, 300, 50,
                           help="Higher values create sharper images but may be slower to render")

        st.markdown("### Title Settings")
        col1, col2 = st.columns(2)
        with col1:
            show_title = st.toggle("Show Title", value=True,
                                 help="Toggle timeline title visibility")
        with col2:
            title_text = st.text_input("Title Text", value="Startup Progress Timeline",
                                     help="Customize the timeline title",
                                     disabled=not show_title)

        st.markdown("### Date Format")
        granularity = st.selectbox(
            "Date Granularity",
            ["Date", "Month", "Quarter", "Year"],
            help="Choose how dates should be displayed"
        )

    with tab3:
        st.markdown("### Timeline Colors")
        col1, col2 = st.columns(2)
        with col1:
            timeline_color = st.color_picker("Timeline", '#14823C',
                                           help="Color of the main timeline line")
            circle_color = st.color_picker("Milestone Circles", '#808080',
                                         help="Color of the milestone circles")
        with col2:
            line_color = st.color_picker("Connecting Lines", '#808080',
                                        help="Color of lines connecting milestones to descriptions")
            background_color = st.color_picker("Background", '#000000',
                                             help="Background color of the timeline")

        st.markdown("### Text Colors")
        col1, col2 = st.columns(2)
        with col1:
            milestone_color = st.color_picker("Descriptions", '#CCCCCC',
                                            help="Color of milestone descriptions")
        with col2:
            date_color = st.color_picker("Dates", '#FFFFFF',
                                        help="Color of dates")

    # Input form
    st.markdown("---")
    st.markdown("### Add New Milestone")
    with st.form("milestone_form"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if granularity == "Date":
                date = st.date_input("Select Date", key="new_date_input")
            elif granularity == "Month":
                date = st.date_input("Select Month", value="today", key="new_month_input")
            elif granularity == "Quarter":
                date = st.date_input("Select Quarter", value="today", key="new_quarter_input")
            else:  # Year
                date = st.date_input("Select Year", value="today", key="new_year_input")
        
        with col2:
            milestone = st.text_area("Milestone Description", key="new_milestone_input",
                                   help="Use Enter/Return key for line breaks")
        
        submitted = st.form_submit_button("Add Milestone")
        
        if submitted and milestone:
            new_milestone = pd.DataFrame({
                'date': [pd.to_datetime(date)],
                'milestone': [milestone]
            })
            if st.session_state.milestones_df.empty:
                st.session_state.milestones_df = new_milestone
            else:
                st.session_state.milestones_df = pd.concat([st.session_state.milestones_df, new_milestone], ignore_index=True)
            save_timeline(st.session_state.milestones_df)

    # Display and edit current milestones
    if not st.session_state.milestones_df.empty:
        st.subheader("Current Milestones")
        
        # Create tabs for viewing and editing
        tab1, tab2 = st.tabs(["View Milestones", "Edit Milestones"])
        
        with tab1:
            # Display current milestones in a table
            display_df = st.session_state.milestones_df.copy()
            display_df['formatted_date'] = display_df['date'].apply(lambda x: format_date(x, granularity))
            st.dataframe(
                display_df[['formatted_date', 'milestone']].rename(columns={'formatted_date': 'Date', 'milestone': 'Milestone'}),
                hide_index=True
            )
            
            # Add refresh button
            if st.button("Refresh Visualization"):
                st.rerun()
            
            # Generate and display timeline
            fig = create_timeline(st.session_state.milestones_df, granularity, 
                                alternate_sides, show_lines, date_distance, 
                                milestone_distance, line_length, dash_density, dpi,
                                milestone_color, line_color, date_color,
                                timeline_color, circle_color, background_color,
                                show_title, title_text)
            if fig:
                st.pyplot(fig, clear_figure=True)  # Add clear_figure=True to prevent memory leaks
        
        with tab2:
            # Edit existing milestones
            for i, row in st.session_state.milestones_df.iterrows():
                with st.expander(f"Edit: {format_date(row['date'], granularity)} - {row['milestone'][:50]}..."):
                    new_date = st.date_input(f"Update Date", value=row['date'], key=f"date_{i}")
                    new_milestone = st.text_area(f"Update Milestone", value=row['milestone'], key=f"milestone_{i}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"Update #{i}", key=f"update_{i}"):
                            st.session_state.milestones_df.loc[i, 'date'] = pd.to_datetime(new_date)
                            st.session_state.milestones_df.loc[i, 'milestone'] = new_milestone
                            save_timeline(st.session_state.milestones_df)
                            st.rerun()
                    with col2:
                        if st.button(f"Delete #{i}", key=f"delete_{i}"):
                            st.session_state.milestones_df = st.session_state.milestones_df.drop(i).reset_index(drop=True)
                            save_timeline(st.session_state.milestones_df)
                            st.rerun()

    # Clear all button
    if st.button("Clear All"):
        if os.path.exists('timeline_data.json'):
            os.remove('timeline_data.json')
        st.session_state.milestones_df = pd.DataFrame(columns=['date', 'milestone'])
        st.rerun()

    # Download button
    if not st.session_state.milestones_df.empty:
        csv = st.session_state.milestones_df.to_csv(index=False)
        st.download_button(
            label="Download Timeline Data",
            data=csv,
            file_name="timeline_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main() 