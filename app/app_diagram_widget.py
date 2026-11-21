"""
================================================================================
File: app/app_diagram_widget.py
Purpose: Create/recreate the winding diagram widget.
Version: 0.1.3
================================================================================
"""

from diagrams.two_layer.two_layer import TwoLayerMotorDiagram
from diagrams.single_layer.single_layer import SingleLayerMotorDiagram
from managers.json_manager import json_manager


def create_diagram_widget(app):
    winding_type = "two_layer"
    if json_manager.project_data:
        winding_type = json_manager.project_data.get(
            "winding_type", "two_layer"
        )
    if winding_type == "single_layer":
        widget = SingleLayerMotorDiagram(size_hint=(1, 1))
    else:
        widget = TwoLayerMotorDiagram(size_hint=(1, 1))
    app.current_winding_type = winding_type
    return widget


def recreate_diagram_widget(app):
    winding_type = "two_layer"
    if json_manager.project_data:
        winding_type = json_manager.project_data.get(
            "winding_type", "two_layer"
        )

    if hasattr(app, "winding_widget"):
        try:
            app.main_layout.remove_widget(app.winding_widget)
        except Exception:
            pass

    app.winding_widget = create_diagram_widget(app)
    app.current_winding_type = winding_type
    app.main_layout.add_widget(app.winding_widget)