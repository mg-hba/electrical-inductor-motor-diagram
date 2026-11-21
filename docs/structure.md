Project Structure - v0.1.3

project/
    main0.1.3.py
    version.py
    requirements.txt
    TODO.md
    README.md
    config.json
    version_info.txt

    assets/
        icons/
            main/
            menu/
            zoom/
            connection/
            conflict/
            app_info/
            docs/
            setup/
            file_ops/
            common/
            misc/
        zarin.png
        app_icon.png
        lap.png
        triangle.png
        concentric.png

    app/                                  (NEW package)
        __init__.py
        main_app.py                       (coordinator)
        app_orientation.py
        app_zoom.py
        app_diagram_widget.py
        app_main_ui.py
        app_actions.py
        app_menu.py
        app_app_info.py
        app_info_labels.py
        app_edit_diagram.py
        app_connection.py
        app_connection_actions.py

    backends/
        __init__.py
        base.py
        vector_backend.py
        null_backend.py

    core/
        __init__.py
        base_diagram_core.py
        view_transform.py
        base_diagram/                     (NEW package)
            __init__.py
            base_diagram.py
            diagram_cutting.py
            diagram_edit_mode.py
            diagram_labels.py
            diagram_table.py
            diagram_connection.py
        connection/
            __init__.py
            models.py
            geometry.py
            topology.py
            topology_ops.py
            conflict_ops.py
            pencil_ops.py
            operations.py
            selection.py
            layer_history.py
            layer_json.py
            layer.py
            renderer.py
        rendering/
            __init__.py
            layer_stack.py
            spatial_hash.py
            canvas_backend.py

    diagrams/
        __init__.py
        base/
            __init__.py
            diagram_base.py
            zoom_controller.py
            touch_handler.py
            layer_renderer.py
            drawing_layer.py
        single_layer/
            __init__.py
            single_layer.py
        two_layer/
            __init__.py
            two_layer.py
        patterns/
            __init__.py
            base_pattern.py
            lap_pattern.py
            triangle_pattern.py
            concentric_pattern.py
            registry.py

    importers/
        __init__.py
        base_importer.py
        importer_registry.py
        svg_importer.py
        dxf_importer.py
        pdf_importer.py
        raster_importer.py

    exporters/
        __init__.py
        vector_exporter.py
        export_dialog.py

    dialogs/
        __init__.py
        project_setup/                    (NEW package)
            __init__.py
            project_setup.py
            setup_project_info.py
            setup_motor_settings.py
            setup_diagram_settings.py
            setup_physical.py
            setup_coil_specs.py
            setup_paper.py
            setup_actions.py
            setup_wire_turns.py
            setup_span_controls.py
            setup_focus_chain.py
            setup_project_data.py
            setup_sections.py
            setup_validation.py
        open_save.py
        file_browser.py
        import_dialog.py
        app_info.py
        docs_viewer.py
        changelog_viewer.py
        jm_setup.py
        log_manager.py
        motor_info.py
        draw_style_dialog.py
        coils_per_pole_dialog.py
        comments_dialog.py
        coming_soon_dialog.py

    managers/
        __init__.py
        json_manager.py
        debug_logger.py
        docs_manager.py

    ui/
        __init__.py
        theme.py
        notifications.py
        components.py
        icon_button.py
        connection_panel.py
        connection_buttons.py
        conflict_dialog.py
        main_menu.py
        zoom_panel.py
        edit_diagram_panel.py             (NEW)

    utils/
        __init__.py
        errors.py
        constants/
            __init__.py
            paper.py
            colors.py
            layout.py
            patterns.py
            connection.py
            project_setup.py
            export.py

    docs/
        index.json
        todo.md
        structure.md
        features.md
        architecture.md
        credits.md
        icon_list.md
        changelog/
            v0.0.1.md ... v0.1.3.md

    logs/

Project Folder Layout (per user project)

    project_name/
        project_name.json
        data/
            diagram (encrypted PNG, no extension)
            diagram.hash (MD5 of content)
