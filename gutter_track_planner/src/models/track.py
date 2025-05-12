class LengthValue:
    """Represents a length in feet and inches."""
    
    def __init__(self, feet=0, inches=0):
        self.feet = feet
        self.inches = inches
        
    @property
    def total_inches(self):
        """Convert to total inches for calculations."""
        return (self.feet * 12) + self.inches
        
    @classmethod
    def from_inches(cls, inches):
        """Create from total inches."""
        feet = int(inches // 12)
        remaining_inches = inches % 12
        return cls(feet, remaining_inches)
    
    def __str__(self):
        return f"{self.feet}' {self.inches}\""


class Track:
    """Represents the gutter track with dimensions."""
    
    def __init__(self, width, depth, lane_width):
        """
        Initialize track dimensions.
        
        Args:
            width (LengthValue): Track width in feet/inches
            depth (LengthValue): Track depth in feet/inches
            lane_width (LengthValue): Minimum lane width in feet/inches
        """
        self.width = width
        self.depth = depth
        self.lane_width = lane_width
        self.pieces = []  # Will hold all placed track pieces
        
    @property
    def grid_size(self):
        """Return the grid size in pixels based on lane width."""
        return self.lane_width.total_inches