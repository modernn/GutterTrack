from typing import Dict, List, Optional, Union
import json
import flet as ft
from models import Track, Piece, PieceType, BillOfMaterials
from utils import calculate_materials_cost

# Since Flet 0.28.2 doesn't have ft.Canvas, we'll handle the BOM calculations directly
# in the main app. But for a real-world app, we'd use FastAPI here.

class BomCalculator:
    """Simplified API-like calculator for bill of materials"""
    
    @staticmethod
    def calculate_bom(track_data: Dict) -> Dict:
        """
        Calculate bill of materials from track data
        
        Args:
            track_data: Track data dictionary
            
        Returns:
            Dictionary with BOM information
        """
        try:
            # Create Track object from data
            track = Track.from_dict(track_data)
            
            # Calculate BOM
            bom = BillOfMaterials(track)
            bom_data = bom.calculate()
            
            # Calculate cost estimate
            cost_data = calculate_materials_cost(bom_data)
            
            # Combine results
            result = {
                "status": "success",
                "bom": bom_data,
                "cost": cost_data
            }
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    def validate_track(track_data: Dict) -> Dict:
        """
        Validate track data
        
        Args:
            track_data: Track data dictionary
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        try:
            # Check required fields
            required_fields = ["width", "depth", "lane_width", "pieces"]
            for field in required_fields:
                if field not in track_data:
                    errors.append(f"Missing required field: {field}")
            
            # If any required fields are missing, return errors
            if errors:
                return {
                    "status": "error",
                    "valid": False,
                    "errors": errors
                }
            
            # Validate dimensions
            if track_data["width"] <= 0:
                errors.append("Width must be greater than zero")
            
            if track_data["depth"] <= 0:
                errors.append("Depth must be greater than zero")
            
            if track_data["lane_width"] <= 0:
                errors.append("Lane width must be greater than zero")
            
            # Validate pieces
            for i, piece_data in enumerate(track_data["pieces"]):
                # Check required piece fields
                piece_fields = ["type", "x", "y", "rotation", "length"]
                for field in piece_fields:
                    if field not in piece_data:
                        errors.append(f"Piece {i+1}: Missing required field: {field}")
                
                # Check piece type
                if "type" in piece_data:
                    valid_types = [
                        "straight", "elbow_22_5", "elbow_45", 
                        "elbow_90", "t_junction"
                    ]
                    if piece_data["type"] not in valid_types:
                        errors.append(f"Piece {i+1}: Invalid type: {piece_data['type']}")
                
                # Check rotation
                if "rotation" in piece_data:
                    valid_rotations = [0, 90, 180, 270]
                    if piece_data["rotation"] not in valid_rotations:
                        errors.append(f"Piece {i+1}: Invalid rotation: {piece_data['rotation']}")
            
            # Return validation result
            return {
                "status": "success",
                "valid": len(errors) == 0,
                "errors": errors
            }
                
        except Exception as e:
            return {
                "status": "error",
                "valid": False,
                "errors": [str(e)]
            }
    
    @staticmethod
    def optimize_track(track_data: Dict) -> Dict:
        """
        Optimize track to minimize material usage
        
        Args:
            track_data: Track data dictionary
            
        Returns:
            Dictionary with optimized track data
        """
        try:
            # Create Track object from data
            track = Track.from_dict(track_data)
            
            # In a real implementation, this would perform optimizations
            # For example:
            # 1. Combine adjacent straight pieces
            # 2. Replace certain combinations of pieces with alternatives
            # 3. Minimize the number of connectors
            
            # For now, just return the original track
            return {
                "status": "success",
                "message": "Track optimization not implemented",
                "track": track_data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    def estimate_assembly_time(track_data: Dict) -> Dict:
        """
        Estimate assembly time based on the track complexity
        
        Args:
            track_data: Track data dictionary
            
        Returns:
            Dictionary with time estimate
        """
        try:
            # Create Track object from data
            track = Track.from_dict(track_data)
            
            # Calculate BOM
            bom = BillOfMaterials(track)
            bom_data = bom.calculate()
            
            # Simple time estimation based on number of pieces
            # In a real implementation, this would be more sophisticated
            
            # Base time in minutes
            base_time = 15
            
            # Time per straight foot (2 minutes per foot)
            straight_time = bom_data["straight_feet"] * 2
            
            # Time per connection (3 minutes per connection)
            connection_time = bom_data["connectors"] * 3
            
            # Time per elbow (additional 1 minute per elbow)
            elbow_time = (
                bom_data["elbows_22_5"] + 
                bom_data["elbows_45"] + 
                bom_data["elbows_90"]
            ) * 1
            
            # Time per T-junction (additional 2 minutes per junction)
            t_junction_time = bom_data["t_junctions"] * 2
            
            # Total time
            total_minutes = base_time + straight_time + connection_time + elbow_time + t_junction_time
            
            # Convert to hours and minutes
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            
            return {
                "status": "success",
                "estimate": {
                    "total_minutes": total_minutes,
                    "hours": hours,
                    "minutes": minutes,
                    "formatted": f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }