# Helpdesk Analytics Dashboard

## Overview
The Helpdesk Analytics Dashboard provides comprehensive insights into ticket management, team performance, response times, and resolution metrics. It includes multiple visualization types and detailed pivot tables for in-depth analysis.

## Features

### 1. **Analytics Fields**
The module automatically tracks the following metrics for each ticket:

- **First Assignment Date** (`assign_date`): Timestamp when the ticket was first assigned to a user
- **Closure Date** (`close_date`): Automatically set when the ticket reaches a closed/folded stage
- **Response Time (Hours)** (`response_time_hours`): Time from ticket creation to first assignment
- **Resolution Time (Hours)** (`resolution_time_hours`): Time from ticket creation to closure

### 2. **Dashboard Views**

#### Graph View
- **Daily Ticket Trends**: Visualize ticket creation patterns over time
- **Tickets by Site**: Compare ticket volumes across different sites
- **Tickets by Department**: Identify busiest departments
- **Tickets by Agent**: Track individual agent workload

#### Pivot Table View
- **Multi-dimensional Analysis**: Analyze tickets by Site × Category × Agent
- **Response Time Metrics**: Average response times by Agent and Site
- **Resolution Time Metrics**: Average resolution times by Agent and Category
- **Custom Grouping**: Group data by any combination of fields

### 3. **Raw Data Export**
Access comprehensive ticket data with all fields available for export:
- Navigate to **Helpdesk → Reports → Raw Data Export**
- All analytics fields included
- One-click Excel export functionality
- Filters available for custom data extractions

### 4. **Performance Indicators**

The ticket form includes an **Analytics tab** with color-coded performance metrics:

**Response Time:**
- 🟢 Green: < 24 hours (Excellent)
- 🟡 Yellow: 24-48 hours (Good)
- 🔴 Red: > 48 hours (Needs Attention)

**Resolution Time:**
- 🟢 Green: < 48 hours (Excellent)
- 🟡 Yellow: 48-96 hours (Good)
- 🔴 Red: > 96 hours (Needs Attention)

## How to Use

### Accessing the Dashboard
1. Open **Helpdesk** application
2. Click **Analytics** in the top menu
3. Choose your preferred view:
   - **Graph View**: For visual trends and comparisons
   - **Pivot View**: For detailed cross-tabulations
   - **List View**: For ticket details with sorting/filtering

### Analyzing Response Times
1. Switch to **Pivot View**
2. Add measures: `Response Time (Hours)` and `Resolution Time (Hours)`
3. Group by:
   - Rows: Agent or Department
   - Columns: Site or Category
4. Identify agents/teams needing support based on higher average times

### Generating Reports

#### Quick Export
1. Go to **Helpdesk → Reports → Raw Data Export**
2. Apply desired filters (date range, site, category, etc.)
3. Click **Export** → **Export All**
4. Open the Excel file with complete ticket data

#### Custom Analysis
1. In **Analytics** view, apply filters in the search bar:
   - Filter by date: "Create Date: Last Month"
   - Filter by site: "Site: is Grand Mall"
   - Filter by status: "Status: is Resolved"
2. Switch between Graph and Pivot views to analyze filtered data
3. Export filtered data using the Export button

### Dashboard JSON (Advanced)
For organizations wanting to create custom OWL dashboards, a template JSON file is available at:
```
osool_helpdesk/data/osool_helpdesk_dashboard.json
```

This file contains 15+ widget configurations including:
- Total Tickets KPI
- Avg Response/Resolution Time KPIs
- Tickets per Agent (Bar Chart)
- Tickets per Department/Site (Pie Charts)
- New vs Completed (Donut Chart)
- Top 10 Owners (Bar Chart)
- Daily/Hourly/Monthly Trends (Line Charts)
- Response/Resolution Time Pivot Tables
- Status Heatmaps

**Note**: OWL dashboard implementation requires Odoo Enterprise Dashboard module and additional customization.

## Automatic Data Collection

### How It Works
The module automatically collects analytics data without manual intervention:

1. **Assignment Tracking**: When a ticket is assigned to a user for the first time, `assign_date` is automatically set
2. **Closure Tracking**: When a ticket moves to a closed/folded stage, `close_date` is automatically set
3. **Time Calculations**: Response and resolution times are computed automatically based on the timestamps

### Data Integrity
- **First Assignment Only**: The `assign_date` captures only the FIRST assignment, even if the ticket is reassigned later
- **Real-time Updates**: Times are calculated in real-time as ticket status changes
- **Stored Values**: All computed metrics are stored in the database for fast querying and reporting

## Best Practices

### For Team Leaders
1. **Daily**: Check Graph View for ticket volume trends
2. **Weekly**: Review Pivot Table for response/resolution times by agent
3. **Monthly**: Export Raw Data for executive reporting
4. **Identify Bottlenecks**: Look for agents/departments with high resolution times

### For Agents
1. **Monitor Your Performance**: Check the Analytics tab on your tickets
2. **Track Response Times**: Aim to assign tickets within 24 hours
3. **Close Tickets Promptly**: Update ticket status to reflect actual completion

### For Administrators
1. **Set SLAs**: Use average response/resolution times to set realistic SLA targets
2. **Resource Planning**: Identify sites/departments needing more support
3. **Training Needs**: Spot agents with consistently high response/resolution times
4. **Trend Analysis**: Use monthly trends to predict seasonal support needs

## Troubleshooting

### Missing Analytics Data
**Issue**: Response time or resolution time shows 0.0
**Solution**: 
- Response time requires `assign_date` to be set (ticket must be assigned to a user)
- Resolution time requires `close_date` to be set (ticket must reach a closed stage)

### Incorrect Time Calculations
**Issue**: Times seem incorrect
**Check**:
1. Verify ticket `create_date` is accurate
2. Check `assign_date` on Analytics tab (should match first assignment)
3. Confirm `close_date` matches when ticket was actually closed
4. Times are in hours, not days (e.g., 25.5 hours = ~1 day)

### Dashboard Not Showing Data
**Issue**: Graph/Pivot views are empty
**Solution**:
1. Remove all filters from the search bar
2. Ensure tickets exist with the fields you're grouping by
3. For time metrics, ensure tickets have been both assigned and closed

## Technical Details

### Database Fields
All new fields are in the `helpdesk.ticket` model:

```python
assign_date = fields.Datetime(
    string='First Assignment Date',
    tracking=True,
    help='Date when ticket was first assigned'
)

close_date = fields.Datetime(
    string='Closure Date',
    compute='_compute_close_date',
    store=True,
    help='Date when ticket was closed'
)

response_time_hours = fields.Float(
    string='Response Time (Hours)',
    compute='_compute_response_time',
    store=True,
    help='Time from creation to assignment in hours'
)

resolution_time_hours = fields.Float(
    string='Resolution Time (Hours)',
    compute='_compute_resolution_time',
    store=True,
    help='Time from creation to closure in hours'
)
```

### Compute Methods
- `_compute_close_date()`: Triggered when `stage_id.fold` becomes True
- `_compute_response_time()`: Calculated from `create_date` to `assign_date`
- `_compute_resolution_time()`: Calculated from `create_date` to `close_date`
- `write()` override: Captures first assignment automatically

### Performance
- All computed fields use `store=True` for database storage
- No real-time computation overhead during queries
- Efficient indexing on date fields for fast reporting
- Suitable for datasets with 100K+ tickets

## Future Enhancements

Planned features for future releases:
- [ ] Real-time dashboard with auto-refresh
- [ ] Email reports with scheduled delivery
- [ ] SLA compliance tracking per ticket
- [ ] Customer satisfaction correlation with response times
- [ ] Agent performance scorecards
- [ ] Predictive analytics for ticket volume forecasting

## Support

For questions or issues with the Analytics Dashboard:
1. Check this documentation first
2. Review the Analytics tab on sample tickets
3. Contact your system administrator
4. Refer to Odoo's official Graph/Pivot view documentation

---

**Version**: 19.0.1.0.3  
**Last Updated**: December 18, 2025  
**Module**: osool_helpdesk
