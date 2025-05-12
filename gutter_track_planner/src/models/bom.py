from models.piece import PieceType

class BillOfMaterials:
    """Calculate bill of materials for a track."""
    
    def __init__(self, track):
        """
        Initialize the BOM calculator.
        
        Args:
            track: The track model
        """
        self.track = track
    
    def calculate(self):
        """
        Calculate the bill of materials.
        
        Returns:
            dict: BOM data
        """
        # Initialize counters
        straight_footage = 0
        elbow_22_count = 0
        elbow_45_count = 0
        elbow_90_count = 0
        tee_count = 0
        
        # Count pieces
        for piece in self.track.pieces:
            if piece.piece_type == PieceType.STRAIGHT:
                straight_footage += piece.length / 12  # Convert to feet
            elif piece.piece_type == PieceType.ELBOW_22:
                elbow_22_count += 1
            elif piece.piece_type == PieceType.ELBOW_45:
                elbow_45_count += 1
            elif piece.piece_type == PieceType.ELBOW_90:
                elbow_90_count += 1
            elif piece.piece_type == PieceType.TEE:
                tee_count += 1
        
        # Calculate connectors (one between each piece)
        connector_count = max(0, len(self.track.pieces) - 1)
        
        # Calculate screws (2 per straight foot, 2 per elbow, 3 per tee)
        screw_count = (
            int(straight_footage * 2) +
            elbow_22_count * 2 +
            elbow_45_count * 2 +
            elbow_90_count * 2 +
            tee_count * 3
        )
        
        return {
            "straight_footage": straight_footage,
            "elbow_22_count": elbow_22_count,
            "elbow_45_count": elbow_45_count,
            "elbow_90_count": elbow_90_count,
            "tee_count": tee_count,
            "connector_count": connector_count,
            "screw_count": screw_count,
        }