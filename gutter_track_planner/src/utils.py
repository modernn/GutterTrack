import json
import os
import base64
from pathlib import Path
import flet as ft

def snap_to_grid(value, grid_size):
    """Snap a coordinate value to the nearest grid point"""
    return round(value / grid_size) * grid_size

def convert_imperial_to_inches(feet, inches=0):
    """Convert feet and inches to total inches"""
    return (feet * 12) + inches

def convert_inches_to_imperial(inches):
    """Convert total inches to feet and inches"""
    feet = int(inches // 12)
    remaining_inches = round(inches % 12, 1)
    return feet, remaining_inches

def validate_dimensions(width, depth, lane_width):
    """Validate track dimensions"""
    errors = []
    
    if width <= 0:
        errors.append("Width must be greater than zero")
    
    if depth <= 0:
        errors.append("Depth must be greater than zero")
    
    if lane_width <= 0:
        errors.append("Lane width must be greater than zero")
    
    # Check if the dimensions are reasonable
    if width > 100:
        errors.append("Width is too large (max 100 feet)")
    
    if depth > 100:
        errors.append("Depth is too large (max 100 feet)")
    
    if lane_width < 2:
        errors.append("Lane width is too small (min 2 inches)")
    
    if lane_width > 24:
        errors.append("Lane width is too large (max 24 inches)")
    
    return errors

def get_app_data_dir():
    """Get the application data directory"""
    # For desktop
    if os.name == 'nt':  # Windows
        app_data = os.getenv('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
        data_dir = os.path.join(app_data, 'GutterTrack')
    else:  # macOS/Linux
        data_dir = os.path.expanduser('~/.guttertrack')
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    return data_dir

def save_track_to_file(track, file_name=None):
    """Save track to a JSON file"""
    data_dir = get_app_data_dir()
    
    if file_name is None:
        file_name = "track.json"
    elif not file_name.endswith('.json'):
        file_name += '.json'
    
    file_path = os.path.join(data_dir, file_name)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(track.to_dict(), f, indent=2)
        return True, file_path
    except Exception as e:
        return False, str(e)

def load_track_from_file(file_path):
    """Load track from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        from models import Track
        track = Track.from_dict(data)
        return True, track
    except Exception as e:
        return False, str(e)

def get_saved_tracks():
    """Get a list of saved tracks"""
    data_dir = get_app_data_dir()
    tracks = []
    
    try:
        for file_name in os.listdir(data_dir):
            if file_name.endswith('.json'):
                file_path = os.path.join(data_dir, file_name)
                tracks.append({
                    'name': file_name,
                    'path': file_path,
                    'date': os.path.getmtime(file_path)
                })
        
        # Sort by date (newest first)
        tracks.sort(key=lambda x: x['date'], reverse=True)
        return tracks
    except Exception:
        return []

def export_track_as_image(track_grid):
    """
    Export track as a PNG image (placeholder function)
    
    In a real implementation, this would use a library to render the grid as an image.
    Since Flet 0.28.2 doesn't support this directly, this is just a placeholder.
    """
    # Placeholder - in a real app, would convert the grid to an image
    return None

def generate_sharing_url(track):
    """
    Generate a URL for sharing the track (placeholder function)
    
    In a real implementation, this would encode the track data in the URL or
    upload it to a server and return a short URL.
    """
    # Simple implementation - encode track data in base64
    track_json = json.dumps(track.to_dict())
    encoded = base64.urlsafe_b64encode(track_json.encode()).decode()
    
    # In a real app, this would be a domain you control
    return f"https://guttertrack.example.com/share/{encoded}"

def get_optimal_cell_size(grid_width, grid_height, container_width, container_height):
    """Calculate the optimal cell size based on grid dimensions and container size"""
    max_cell_width = container_width / grid_width if grid_width > 0 else 40
    max_cell_height = container_height / grid_height if grid_height > 0 else 40
    
    # Take the minimum to ensure the grid fits in both dimensions
    cell_size = min(max_cell_width, max_cell_height)
    
    # Ensure a reasonable size (between 20 and 60 pixels)
    return max(20, min(60, cell_size))

def calculate_materials_cost(bom, prices=None):
    """
    Calculate the cost of materials based on the bill of materials
    
    Args:
        bom: Dictionary containing the bill of materials
        prices: Dictionary with unit prices (optional, uses defaults if None)
    
    Returns:
        Dictionary with cost breakdown and total
    """
    # Default prices in USD
    default_prices = {
        "straight_foot": 3.50,  # Price per foot of straight gutter
        "elbow_22_5": 3.99,    # Price per 22.5° elbow
        "elbow_45": 4.49,      # Price per 45° elbow
        "elbow_90": 4.99,      # Price per 90° elbow
        "t_junction": 7.99,    # Price per T-junction
        "connector": 1.99,     # Price per connector
        "screw": 0.10          # Price per screw
    }
    
    # Use provided prices or defaults
    if prices is None:
        prices = default_prices
    else:
        # Merge with defaults for any missing prices
        for key, value in default_prices.items():
            if key not in prices:
                prices[key] = value
    
    # Calculate costs
    straight_cost = bom["straight_feet"] * prices["straight_foot"]
    elbows_22_5_cost = bom["elbows_22_5"] * prices["elbow_22_5"]
    elbows_45_cost = bom["elbows_45"] * prices["elbow_45"]
    elbows_90_cost = bom["elbows_90"] * prices["elbow_90"]
    t_junctions_cost = bom["t_junctions"] * prices["t_junction"]
    connectors_cost = bom["connectors"] * prices["connector"]
    screws_cost = bom["screws"] * prices["screw"]
    
    # Calculate total
    total_cost = (
        straight_cost + 
        elbows_22_5_cost + 
        elbows_45_cost + 
        elbows_90_cost + 
        t_junctions_cost + 
        connectors_cost + 
        screws_cost
    )
    
    return {
        "straight": round(straight_cost, 2),
        "elbows_22_5": round(elbows_22_5_cost, 2),
        "elbows_45": round(elbows_45_cost, 2),
        "elbows_90": round(elbows_90_cost, 2),
        "t_junctions": round(t_junctions_cost, 2),
        "connectors": round(connectors_cost, 2),
        "screws": round(screws_cost, 2),
        "total": round(total_cost, 2)
    }

def format_currency(amount):
    """Format an amount as USD currency"""
    return f"${amount:.2f}"

def create_error_snackbar(page, message):
    """Create and show an error snackbar"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.colors.RED
    )
    page.snack_bar.open = True
    page.update()

def create_success_snackbar(page, message):
    """Create and show a success snackbar"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.colors.GREEN
    )
    page.snack_bar.open = True
    page.update()