import flet as ft
import math
import traceback
import sys
from models.track import Track
from models.piece import Piece, PieceType, StraightPiece, ElbowPiece, TeePiece
from utils.grid import snap_to_grid, is_position_valid
from views.draggable_piece import DraggablePiece

class TrackCanvas(ft.Control):
    def _get_control_name(self):
        return "track-canvas"
    
    def __init__(self, track):
        super().__init__()
        self.track = track
        self.scale = 1.0
        self.pieces = []
        self.selected_piece = None
        
    def build(self):
        self.piece_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        self.track_info = ft.Column([
            ft.Text(f"Track dimensions:", size=16, weight="bold"),
            ft.Text(f"Width: {self.track.width}"),
            ft.Text(f"Depth: {self.track.depth}"),
            ft.Text(f"Lane Width: {self.track.lane_width}"),
        ])
        
        return ft.Container(
            content=ft.Column([
                self.track_info,
                ft.Divider(),
                self.piece_list,
            ]),
            bgcolor="#1E1E1E",
            border_radius=10,
            padding=20,
            width=800,
            height=400,
        )
    
    def add_piece(self, piece):
        """Add a piece to the track."""
        self.track.pieces.append(piece)
        self.update_visualization()
    
    def update_visualization(self):
        """Update the piece list visualization."""
        self.piece_list.controls.clear()
        
        for i, piece in enumerate(self.track.pieces):
            is_selected = (piece == self.selected_piece)
            
            piece_item = ft.Container(
                content=ft.Row([
                    ft.Icon(
                        name="check_box" if is_selected else "check_box_outline_blank",
                        color="#9C27B0" if is_selected else "#9E9E9E",
                    ),
                    ft.Column([
                        ft.Text(f"{piece.piece_type.value.capitalize()}", weight="bold"),
                        ft.Text(f"Position: ({piece.position[0]}, {piece.position[1]})"),
                        ft.Text(f"Rotation: {piece.rotation}°, Flipped: {piece.flipped}"),
                    ]),
                ]),
                bgcolor="#333333" if is_selected else "transparent",
                border_radius=5,
                padding=10,
                on_click=lambda e, p=piece: self.select_piece(p),
            )
            
            self.piece_list.controls.append(piece_item)
        
        self.update()
    
    def select_piece(self, piece):
        """Select a piece."""
        self.selected_piece = piece
        self.update_visualization()