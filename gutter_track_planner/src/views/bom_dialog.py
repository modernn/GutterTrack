import flet as ft
from models.bom import BillOfMaterials

class BOMDialog(ft.AlertDialog):
    def _get_control_name(self):
        return "bom-dialog"
    
    def __init__(self, track):
        # Calculate BOM
        bom = self._calculate_bom(track)
        
        # Create content
        content = ft.Column([
            ft.Text("Bill of Materials", size=20, weight="bold"),
            ft.Divider(),
            ft.Row([ft.Text("Straight Gutter:", width=200), ft.Text(f"{bom['straight_footage']:.1f} feet")]),
            ft.Row([ft.Text("22.5° Elbows:", width=200), ft.Text(str(bom["elbow_22_count"]))]),
            ft.Row([ft.Text("45° Elbows:", width=200), ft.Text(str(bom["elbow_45_count"]))]),
            ft.Row([ft.Text("90° Elbows:", width=200), ft.Text(str(bom["elbow_90_count"]))]),
            ft.Row([ft.Text("T-Junctions:", width=200), ft.Text(str(bom["tee_count"]))]),
            ft.Divider(),
            ft.Row([ft.Text("Connectors:", width=200), ft.Text(str(bom["connector_count"]))]),
            ft.Row([ft.Text("Screws:", width=200), ft.Text(str(bom["screw_count"]))]),
        ])
        
        super().__init__(
            title=ft.Text("Bill of Materials"),
            content=content,
            actions=[
                ft.TextButton("Close", on_click=self._on_close),
            ],
            actions_alignment="end",
        )
    
    def _calculate_bom(self, track):
        # BOM calculation logic
        straight_footage = 0
        elbow_22_count = 0
        elbow_45_count = 0
        elbow_90_count = 0
        tee_count = 0
        
        for piece in track.pieces:
            if piece.piece_type == PieceType.STRAIGHT:
                straight_footage += piece.length / 12
            elif piece.piece_type == PieceType.ELBOW_22:
                elbow_22_count += 1
            elif piece.piece_type == PieceType.ELBOW_45:
                elbow_45_count += 1
            elif piece.piece_type == PieceType.ELBOW_90:
                elbow_90_count += 1
            elif piece.piece_type == PieceType.TEE:
                tee_count += 1
        
        connector_count = max(0, len(track.pieces) - 1)
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
    
    def _on_close(self, e):
        self.open = False
        self.update()