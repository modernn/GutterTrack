def snap_to_grid(x, y, grid_size=1.0):
    """
    Snap coordinates to the nearest grid point.
    
    Args:
        x (float): X coordinate
        y (float): Y coordinate
        grid_size (float): Grid size
        
    Returns:
        tuple: Snapped (x, y) coordinates
    """
    snapped_x = round(x / grid_size) * grid_size
    snapped_y = round(y / grid_size) * grid_size
    return snapped_x, snapped_y


def is_position_valid(track, piece, position):
    """
    Check if a piece placement is valid.
    
    Args:
        track (Track): The track model
        piece: The piece to check
        position (tuple): The position to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Check if position is within track bounds
        width_grid = track.width.total_inches / track.lane_width.total_inches
        depth_grid = track.depth.total_inches / track.lane_width.total_inches
        
        x, y = position
        
        # Simple boundary check for now
        if x < 0 or x > width_grid or y < 0 or y > depth_grid:
            return False
        
        # For now, just return True for all placements within bounds
        # We'll implement the full lane width validation later
        return True
    except Exception as e:
        # Log the error but return False for safety
        print(f"Error validating position: {e}")
        return False