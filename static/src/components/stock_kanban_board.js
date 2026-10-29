/** @odoo-module **/

import { Component, useState, onWillStart, onWillDestroy } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * Componente principal del Tablero Kanban OWL v2
 * Gestiona la visualización reactiva del stock de productos clasificados por nivel de riesgo,
 * con soporte responsivo móvil y suscripción en tiempo real al bus de Odoo.
 */
export class StockKanbanBoard extends Component {
    static template = "kanban_owl_v2.StockKanbanBoard";

    setup() {
        // Conexión con los servicios estándar de Odoo
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");

        // En Odoo 17, bus_service se accede directamente vía this.env.services
        this.busService = this.env.services.bus_service;

        // Estado reactivo de la vista
        this.state = useState({
            products: [],          // Lista general de productos
            searchQuery: "",       // Texto ingresado en el buscador
            filterStatus: "all",   // Filtro móvil/pestaña ('all', 'critical', 'warning', 'optimal')
            isLoading: true,       // Indicador de carga inicial
            processingId: null,    // ID del producto en proceso de reabastecimiento
        });

        // Suscripción al canal de eventos del Bus de Odoo (WebSockets / Longpolling)
        this.busChannel = "stock_health_channel";
        if (this.busService) {
            this.busService.addChannel(this.busChannel);

            this.onStockUpdated = () => {
                // Actualización reactiva sin mostrar spinner de pantalla completa
                this.loadProducts({ silent: true });
            };
            this.busService.subscribe("stock_updated", this.onStockUpdated);
        }

        // Cargar los productos al iniciar el componente
        onWillStart(async () => {
            await this.loadProducts();
        });

        // Limpieza de suscripción al desmontar el componente
        onWillDestroy(() => {
            if (this.busService && this.busService.deleteChannel) {
                this.busService.deleteChannel(this.busChannel);
            }
        });
    }

    /**
     * Consulta los productos almacenables al backend mediante el ORM de Odoo.
     * @param {Object} options - silent: true para refresco en segundo plano sin spinner.
     */
    async loadProducts(options = {}) {
        try {
            if (!options.silent) {
                this.state.isLoading = true;
            }
            const domain = [
                ["type", "in", ["product", "consu"]],
                ["active", "=", true]
            ];
            const fields = [
                "id",
                "name",
                "default_code",
                "qty_available",
                "uom_id",
                "x_min_security_stock",
                "x_stock_health_status",
                "x_replenish_requested",
                "write_date",
            ];

            const result = await this.orm.searchRead("product.template", domain, fields, {
                order: "qty_available asc, name asc",
            });

            this.state.products = result;
        } catch (error) {
            console.error("Error al cargar los productos:", error);
            if (!options.silent) {
                this.notification.add("No se pudieron cargar los datos de inventario.", {
                    type: "danger",
                    title: "Error de conexión",
                });
            }
        } finally {
            if (!options.silent) {
                this.state.isLoading = false;
            }
        }
    }

    /**
     * Filtra los productos en tiempo real según el texto escrito en el buscador.
     */
    get filteredProducts() {
        const query = (this.state.searchQuery || "").trim().toLowerCase();
        if (!query) {
            return this.state.products;
        }
        return this.state.products.filter((p) => {
            const nameMatch = (p.name || "").toLowerCase().includes(query);
            const codeMatch = (p.default_code || "").toLowerCase().includes(query);
            return nameMatch || codeMatch;
        });
    }

    // Listas agrupadas automáticamente para cada una de las 3 columnas
    get criticalProducts() {
        return this.filteredProducts.filter((p) => p.x_stock_health_status === "critical");
    }

    get warningProducts() {
        return this.filteredProducts.filter((p) => p.x_stock_health_status === "warning");
    }

    get optimalProducts() {
        return this.filteredProducts.filter((p) => p.x_stock_health_status === "optimal");
    }

    // Contadores para los indicadores rápidos en la barra superior
    get totalCount() {
        return this.filteredProducts.length;
    }

    get criticalCount() {
        return this.criticalProducts.length;
    }

    get warningCount() {
        return this.warningProducts.length;
    }

    get optimalCount() {
        return this.optimalProducts.length;
    }

    /**
     * Cambia la pestaña o filtro visual en modo móvil.
     */
    setMobileFilter(status) {
        this.state.filterStatus = status;
    }

    /**
     * Limpia el campo de búsqueda rápida.
     */
    clearSearch() {
        this.state.searchQuery = "";
    }

    /**
     * Abre el formulario estándar de Odoo para consultar o editar el producto.
     */
    openProductForm(productId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "product.template",
            res_id: productId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /**
     * Dispara la acción RPC en el servidor para crear una orden de movimiento real de inventario.
     */
    async onReplenishQuick(product, ev) {
        if (ev) {
            ev.stopPropagation(); // Evita abrir el formulario al presionar el botón
        }

        try {
            this.state.processingId = product.id;

            // Llamada al método Python definido en el modelo
            const result = await this.orm.call(
                "product.template",
                "action_replenish_quick",
                [[product.id]]
            );

            // Notificación visual de éxito para el usuario
            this.notification.add(
                result.message || `Orden de inventario generada para ${product.name}`,
                {
                    type: "success",
                    title: "Reabastecimiento Creado",
                    sticky: false,
                }
            );

            // Actualizamos el estado local del producto
            product.x_replenish_requested = true;

            // Recargamos datos en segundo plano
            await this.loadProducts({ silent: true });
        } catch (error) {
            console.error("Error al reabastecer el producto:", error);
            const msg = error.data?.message || error.message || "Error al procesar la solicitud.";
            this.notification.add(msg, {
                type: "danger",
                title: "No se pudo crear la orden",
            });
        } finally {
            this.state.processingId = null;
        }
    }
}

// Registro de la acción cliente en el sistema web de Odoo
registry.category("actions").add("kanban_owl_v2.stock_board", StockKanbanBoard);
