from enum import Enum

class PieceType(Enum):
    STRAIGHT = "straight"
    ELBOW_22_5 = "elbow_22_5"
    ELBOW_45 = "elbow_45"
    ELBOW_90 = "elbow_90"
    T_JUNCTION = "t_junction"

class Piece:
    def __init__(self, piece_type, x=0, y=0, rotation=0, length=1):
        self.type = piece_type
        self.x = x
        self.y = y
        self.rotation = rotation  # In degrees (0, 90, 180, 270)
        self.length = length if piece_type == PieceType.STRAIGHT else 1
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "length": self.length
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            piece_type=PieceType(data["type"]),
            x=data["x"],
            y=data["y"],
            rotation=data["rotation"],
            length=data["length"]
        )
        
    def rotate(self, degrees=90):
        """Rotate the piece by specified degrees clockwise"""
        self.rotation = (self.rotation + degrees) % 360
        
    def get_occupied_cells(self, grid_size):
        """Return list of grid cells this piece occupies"""
        cells = []
        grid_x = int(self.x / grid_size)
        grid_y = int(self.y / grid_size)
        
        # Base cell
        cells.append((grid_x, grid_y))
        
        # Additional cells based on piece type and rotation
        if self.type == PieceType.STRAIGHT:
            # For straight pieces, add cells based on length and rotation
            if self.rotation in [0, 180]:  # Horizontal
                for i in range(1, self.length):
                    cells.append((grid_x + i, grid_y))
            else:  # Vertical (90, 270)
                for i in range(1, self.length):
                    cells.append((grid_x, grid_y + i))
        elif self.type in [PieceType.ELBOW_45, PieceType.ELBOW_90]:
            # For elbows, add one more cell based on rotation
            if self.rotation == 0:  # Right and down
                cells.append((grid_x + 1, grid_y + 1))
            elif self.rotation == 90:  # Left and down
                cells.append((grid_x - 1, grid_y + 1))
            elif self.rotation == 180:  # Left and up
                cells.append((grid_x - 1, grid_y - 1))
            elif self.rotation == 270:  # Right and up
                cells.append((grid_x + 1, grid_y - 1))
        elif self.type == PieceType.T_JUNCTION:
            # T junction has three connecting points
            if self.rotation == 0:  # T pointing down
                cells.extend([(grid_x - 1, grid_y), (grid_x + 1, grid_y), (grid_x, grid_y + 1)])
            elif self.rotation == 90:  # T pointing left
                cells.extend([(grid_x, grid_y - 1), (grid_x, grid_y + 1), (grid_x - 1, grid_y)])
            elif self.rotation == 180:  # T pointing up
                cells.extend([(grid_x - 1, grid_y), (grid_x + 1, grid_y), (grid_x, grid_y - 1)])
            elif self.rotation == 270:  # T pointing right
                cells.extend([(grid_x, grid_y - 1), (grid_x, grid_y + 1), (grid_x + 1, grid_y)])
                
        return cells

class Track:
    def __init__(self, width, depth, lane_width):
        self.width = width  # In feet
        self.depth = depth  # In feet
        self.lane_width = lane_width  # In inches
        self.pieces = []
        
        # Calculate grid dimensions
        self.grid_width = int(width * 12 / lane_width)  # Columns
        self.grid_height = int(depth * 12 / lane_width)  # Rows
    
    def add_piece(self, piece):
        """Add a piece to the track if it doesn't overlap with existing pieces"""
        if self.can_place_piece(piece):
            self.pieces.append(piece)
            return True
        return False
    
    def remove_piece(self, piece):
        """Remove a piece from the track"""
        if piece in self.pieces:
            self.pieces.remove(piece)
            return True
        return False
    
    def piece_at_position(self, grid_x, grid_y):
        """Find if there's a piece at the given grid position"""
        for piece in self.pieces:
            occupied_cells = piece.get_occupied_cells(self.lane_width)
            if (grid_x, grid_y) in occupied_cells:
                return piece
        return None
    
    def can_place_piece(self, piece):
        """Check if a piece can be placed without overlap"""
        occupied_cells = piece.get_occupied_cells(self.lane_width)
        
        # Check grid boundaries
        for cell_x, cell_y in occupied_cells:
            if cell_x < 0 or cell_x >= self.grid_width or cell_y < 0 or cell_y >= self.grid_height:
                return False
        
        # Check for overlap with existing pieces
        for existing_piece in self.pieces:
            if existing_piece == piece:  # Skip the piece itself
                continue
                
            existing_cells = existing_piece.get_occupied_cells(self.lane_width)
            for cell in occupied_cells:
                if cell in existing_cells:
                    return False
        
        return True
    
    def to_dict(self):
        """Convert track to dictionary for serialization"""
        return {
            "width": self.width,
            "depth": self.depth,
            "lane_width": self.lane_width,
            "pieces": [piece.to_dict() for piece in self.pieces]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a track from a dictionary representation"""
        track = cls(
            width=data["width"],
            depth=data["depth"],
            lane_width=data["lane_width"]
        )
        
        for piece_data in data["pieces"]:
            track.add_piece(Piece.from_dict(piece_data))
        
        return track

class BillOfMaterials:
    def __init__(self, track):
        self.track = track
    
    def calculate(self):
        """Calculate the bill of materials based on the pieces in the track"""
        # Initialize counters
        straight_feet = 0
        elbows_22_5 = 0
        elbows_45 = 0
        elbows_90 = 0
        t_junctions = 0
        
        # Count pieces
        for piece in self.track.pieces:
            if piece.type == PieceType.STRAIGHT:
                # Convert to feet (lane width is in inches)
                piece_length_feet = (piece.length * self.track.lane_width) / 12
                straight_feet += piece_length_feet
            elif piece.type == PieceType.ELBOW_22_5:
                elbows_22_5 += 1
            elif piece.type == PieceType.ELBOW_45:
                elbows_45 += 1
            elif piece.type == PieceType.ELBOW_90:
                elbows_90 += 1
            elif piece.type == PieceType.T_JUNCTION:
                t_junctions += 1
        
        # Calculate connectors and screws
        # This is a simplified calculation - in reality, it would depend on the specific connections
        total_pieces = len(self.track.pieces)
        connectors = max(0, total_pieces - 1)
        screws = connectors * 2  # Assuming each connector needs two screws
        
        return {
            "straight_feet": round(straight_feet, 2),
            "elbows_22_5": elbows_22_5,
            "elbows_45": elbows_45,
            "elbows_90": elbows_90,
            "t_junctions": t_junctions,
            "connectors": connectors,
            "screws": screws
        }