/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class HelpdeskAnalyticsDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = useState({
            totalTickets: 0,
            openTickets: 0,
            closedTickets: 0,
            avgResponseTime: 0,
            avgResolutionTime: 0,
            ticketsByAgent: [],
            ticketsByDepartment: [],
            ticketsBySite: [],
            ticketsByStatus: [],
            ticketsByCategory: [],
            topOwners: [],
            dailyTrend: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Total Tickets
            const totalTickets = await this.orm.searchCount("helpdesk.ticket", []);
            
            // Open Tickets (not folded stages)
            const openTickets = await this.orm.searchCount("helpdesk.ticket", [["stage_id.fold", "=", false]]);
            
            // Closed Tickets (folded stages)
            const closedTickets = await this.orm.searchCount("helpdesk.ticket", [["stage_id.fold", "=", true]]);
            
            // Avg Response Time
            const responseData = await this.orm.readGroup(
                "helpdesk.ticket",
                [["response_time_hours", ">", 0]],
                ["response_time_hours:avg"],
                []
            );
            const avgResponseTime = responseData.length > 0 ? responseData[0].response_time_hours : 0;

            // Avg Resolution Time
            const resolutionData = await this.orm.readGroup(
                "helpdesk.ticket",
                [["resolution_time_hours", ">", 0]],
                ["resolution_time_hours:avg"],
                []
            );
            const avgResolutionTime = resolutionData.length > 0 ? resolutionData[0].resolution_time_hours : 0;

            // Tickets by Agent (sorted by count)
            const ticketsByAgent = await this.orm.readGroup(
                "helpdesk.ticket",
                [["user_id", "!=", false]],
                ["user_id"],
                ["user_id"],
                { orderby: "__count desc" }
            );

            // Tickets by Department (sorted by count)
            const ticketsByDepartment = await this.orm.readGroup(
                "helpdesk.ticket",
                [["team_department_id", "!=", false]],
                ["team_department_id"],
                ["team_department_id"],
                { orderby: "__count desc" }
            );

            // Tickets by Site (sorted by count)
            const ticketsBySite = await this.orm.readGroup(
                "helpdesk.ticket",
                [["site_id", "!=", false]],
                ["site_id"],
                ["site_id"],
                { orderby: "__count desc" }
            );

            // Tickets by Category (sorted by count)
            const ticketsByCategory = await this.orm.readGroup(
                "helpdesk.ticket",
                [["request_category_id", "!=", false]],
                ["request_category_id"],
                ["request_category_id"],
                { orderby: "__count desc", limit: 10 }
            );

            // Tickets by Status
            const ticketsByStatus = await this.orm.readGroup(
                "helpdesk.ticket",
                [],
                ["stage_id"],
                ["stage_id"],
                { orderby: "__count desc" }
            );

            // Top 10 Owners
            const topOwners = await this.orm.readGroup(
                "helpdesk.ticket",
                [["user_id", "!=", false]],
                ["user_id"],
                ["user_id"],
                { limit: 10, orderby: "__count desc" }
            );

            // Daily Trend (last 30 days)
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            const dailyTrend = await this.orm.readGroup(
                "helpdesk.ticket",
                [["create_date", ">=", thirtyDaysAgo.toISOString()]],
                ["create_date:day"],
                ["create_date:day"]
            );

            Object.assign(this.state, {
                totalTickets,
                openTickets,
                closedTickets,
                avgResponseTime: Math.round(avgResponseTime * 10) / 10,
                avgResolutionTime: Math.round(avgResolutionTime * 10) / 10,
                ticketsByAgent,
                ticketsByDepartment,
                ticketsBySite,
                ticketsByStatus,
                ticketsByCategory,
                topOwners,
                dailyTrend,
                loading: false,
            });
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }

    openTickets(domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Tickets",
            res_model: "helpdesk.ticket",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            context: {},
        });
    }

    getChartColor(index) {
        const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];
        return colors[index % colors.length];
    }
}

HelpdeskAnalyticsDashboard.template = "osool_helpdesk.HelpdeskAnalyticsDashboard";

registry.category("actions").add("helpdesk_analytics_dashboard", HelpdeskAnalyticsDashboard);
