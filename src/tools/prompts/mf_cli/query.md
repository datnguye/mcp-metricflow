# Query Metrics

## Purpose
Use this tool to query metrics and dimensions from your MetricFlow semantic layer. This tool executes MetricFlow queries and returns the results as structured data.

## When to Use
- When you need to retrieve metric values with optional dimensional breakdowns
- When you want to analyze data with time-based filtering
- When you need to apply SQL-like WHERE conditions to filter results
- When you want to order and limit query results

## Parameters

### Required Parameters
- **session_id**: A unique identifier for this query session (used for tracking and result management)
- **metrics**: List of metric names to query (e.g., `["revenue", "customer_count"]`)
  - Either `metrics` or `saved_query` must be provided

### Optional Parameters
- **group_by**: List of dimensions or entities to group by (e.g., `["date", "country"]`)
- **start_time**: ISO8601 timestamp for the start of the time range (inclusive)
- **end_time**: ISO8601 timestamp for the end of the time range (inclusive)
- **where**: SQL-like WHERE clause to filter results (e.g., `"revenue > 1000"`)
- **order**: List of fields to order by, use `-` prefix for DESC (e.g., `["-date", "revenue"]`)
- **limit**: Maximum number of rows to return (default: 100, set to `null` for no limit)
- **saved_query**: Name of a pre-defined saved query to execute
- **explain**: Show the SQL query that was executed (default: false)
- **show_dataflow_plan**: Display the dataflow plan in explain output (default: false)
- **show_sql_descriptions**: Show inline descriptions of nodes in SQL (default: false)

## Examples

### Basic Metric Query
```json
{
  "session_id": "session_123",
  "metrics": ["revenue", "order_count"]
}
```

### Query with Dimensional Breakdown
```json
{
  "session_id": "session_124",
  "metrics": ["revenue"],
  "group_by": ["date", "product_category"]
}
```

### Time-Filtered Query
```json
{
  "session_id": "session_125",
  "metrics": ["daily_active_users"],
  "group_by": ["date"],
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-31T23:59:59Z"
}
```

### Query with WHERE Clause and Ordering
```json
{
  "session_id": "session_126",
  "metrics": ["revenue", "profit_margin"],
  "group_by": ["region", "product_line"],
  "where": "revenue > 10000 AND region != 'TEST'",
  "order": ["-revenue", "region"],
  "limit": 50
}
```

### Using a Saved Query
```json
{
  "session_id": "session_127",
  "saved_query": "monthly_revenue_by_region"
}
```

## Output Format
The tool returns a tuple of (message, data):
- **message**: JSON string containing execution information and any errors
- **data**: JSON string containing the query results as an array of objects

## Best Practices
1. Always provide a unique session_id for tracking purposes
2. Use descriptive metric and dimension names that match your semantic model
3. Apply time filters when querying large datasets to improve performance
4. Use WHERE clauses for additional filtering beyond time ranges
5. Set appropriate limits to manage result size
6. Use saved queries for frequently executed complex queries