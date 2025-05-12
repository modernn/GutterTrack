import flet as ft
from models.bom import BillOfMaterials

class BOMDialog(ft.AlertDialog):
    """Dialog to display bill of materials."""
    
    def __init__(self, track):
        """
        Initialize the BOM dialog.
        
        Args:
            track: The track model
        """
        # Calculate BOM
        bom = BillOfMaterials(track).calculate()
        
        # Create content
        content = ft.Column(
            controls=[
                ft.Text("Bill of Materials", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self._create_bom_row("Straight Gutter:", f"{bom['straight_footage']:.1f} feet"),
                self._create_bom_row("22.5° Elbows:", str(bom["elbow_22_count"])),
                self._create_bom_row("45° Elbows:", str(bom["elbow_45_count"])),
                self._create_bom_row("90° Elbows:", str(bom["elbow_90_count"])),
                self._create_bom_row("T-Junctions:", str(bom["tee_count"])),
                ft.Divider(),
                self._create_bom_row("Connectors:", str(bom["connector_count"])),
                self._create_bom_row("Screws:", str(bom["screw_count"])),
            ],
            width=400,
        )
        
        super().__init__(
            title=ft.Text("Bill of Materials"),
            content=content,
            actions=[
                ft.TextButton("Export", on_click=self._on_export),
                ft.TextButton("Close", on_click=self._on_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _create_bom_row(self, label, value):
        """Create a row for the BOM table."""
        return ft.Row(
            controls=[
                ft.Text(label, weight=ft.FontWeight.BOLD, width=150),
                ft.Text(value),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
    
    def _on_export(self, e):
        """Handle export button click."""
        # TODO: Implement export functionality
        pass
    
    def _on_close(self, e):
        """Handle close button click."""
        self.open = False
        self.update()