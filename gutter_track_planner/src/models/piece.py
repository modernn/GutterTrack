from enum import Enum

class PieceType(Enum):
    STRAIGHT = "straight"
    ELBOW_22 = "elbow_22"
    ELBOW_45 = "elbow_45"
    ELBOW_90 = "elbow_90"
    TEE = "tee"

class Piece:
    """Base class for track pieces."""
    
    def __init__(self, piece_type, position=(0, 0), rotation=0, flipped=False):
        """
        Initialize a track piece.
        
        Args:
            piece_type (PieceType): Type of piece
            position (tuple): (x, y) position in grid coordinates
            rotation (int): Rotation in degrees (0, 90, 180, 270)
            flipped (bool): Whether the piece is flipped
        """
        self.piece_type = piece_type
        self.position = position
        self.rotation = rotation
        self.flipped = flipped
        
    def rotate(self, clockwise=True):
        """Rotate the piece 90 degrees."""
        delta = 90 if clockwise else -90
        self.rotation = (self.rotation + delta) % 360
        
    def flip(self):
        """Flip the piece."""
        self.flipped = not self.flipped


class StraightPiece(Piece):
    """Straight piece with variable length."""
    
    def __init__(self, length, **kwargs):
        """
        Initialize a straight piece.
        
        Args:
            length (float): Length in inches
            **kwargs: Other piece parameters
        """
        super().__init__(PieceType.STRAIGHT, **kwargs)
        self.length = length


class ElbowPiece(Piece):
    """Elbow piece with specific angle."""
    
    def __init__(self, angle, **kwargs):
        """
        Initialize an elbow piece.
        
        Args:
            angle (int): Angle in degrees (22.5, 45, 90)
            **kwargs: Other piece parameters
        """
        if angle == 22.5:
            piece_type = PieceType.ELBOW_22
        elif angle == 45:
            piece_type = PieceType.ELBOW_45
        else:  # Default to 90
            piece_type = PieceType.ELBOW_90
            
        super().__init__(piece_type, **kwargs)
        self.angle = angle


class TeePiece(Piece):
    """T-junction piece."""
    
    def __init__(self, **kwargs):
        """Initialize a tee piece."""
        super().__init__(PieceType.TEE, **kwargs)