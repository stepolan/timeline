# Timeline Generator

A Streamlit-based timeline visualization tool that allows users to create, edit, and visualize milestone timelines with a clean, modern interface.

## Features

- Interactive timeline creation and editing
- Automatic past/future milestone styling
- Customizable layout options:
  - Alternating milestone positions
  - Adjustable distances for dates and descriptions
  - Configurable connecting lines
  - Customizable dash patterns for future timeline segments
- Date granularity options (Date/Month/Quarter/Year)
- Import/Export functionality (CSV)
- Data persistence (JSON)
- Dark theme optimized

## Installation

1. Clone the repository:
```bash
git clone https://github.com/stepolan/timeline.git
cd timeline
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Controls

- **Date Distance**: Adjust the distance of dates from the timeline
- **Description Distance**: Adjust the distance of milestone descriptions
- **Line Length**: Control the length of connecting lines
- **Dash Density**: Adjust the density of dashes in future timeline segments
- **Toggle Options**: 
  - Alternate milestone positions
  - Show/hide connecting lines

## Data Management

- Data is automatically saved to `timeline_data.json`
- Export your timeline to CSV
- Import existing timelines from CSV (must have 'date' and 'milestone' columns)

## License

MIT License - feel free to use and modify as needed. 