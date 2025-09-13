/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MiKanbanComponente extends Component {
    static template = "mi_kanban_basico.MiKanbanComponente";
    
    setup() {
        this.orm = useService("orm"); // Usar ORM service en lugar de RPC directo
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            elementos: [],
            cargando: true,
            error: null,
        });


        onWillStart(async () => {
            await this.cargarElementos();
        });
    }

    async cargarElementos() {
        try {
            this.state.cargando = true;
            this.state.error = null;
            
            // Usar el servicio ORM para buscar elementos
            this.state.elementos = await this.orm.searchRead(
                "mi.modelo",
                [],
                ["id", "name", "image", "descripcion"]
            );
            
            console.log("Elementos cargados:", this.state.elementos);
            
        } catch (error) {
            console.error("Error detallado al cargar elementos:", error);
            this.state.error = "Error al cargar elementos: " + error.message;
            this.notification.add(
                this.state.error,
                { type: "danger", title: "Error" }
            );
        } finally {
            this.state.cargando = false;
        }
    }

    abrirFormularioNuevo = () => {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mi.modelo",
            views: [[false, "form"]],
            target: "new",
        });
    }

    abrirElemento = (elemento) => {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mi.modelo",
            res_id: elemento.id,
            views: [[false, "form"]],
            target: "new",
        });
    }

    // Función para recargar los elementos
    recargarElementos() {
        this.cargarElementos();
    }
}

registry.category("actions").add("mi_kanban_basico.MiKanbanComponente", MiKanbanComponente);