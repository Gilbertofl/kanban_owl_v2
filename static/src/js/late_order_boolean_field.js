/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class SimpleFixedWidget extends Component {
    static template = "mi_kanban_basico.SimpleFixedWidget";
    static props = { ...standardFieldProps };

    setup() {
        // Contenido fijo - no necesita lógica especial
        console.log("Widget fijo inicializado");
    }
}

export const simpleFixedDescriptor = {
  component: SimpleFixedWidget,
  displayName: "Texto Fijo",
  supportedTypes: ["char", "text"],
};

registry.category("fields").add("simple_fixed", simpleFixedDescriptor);