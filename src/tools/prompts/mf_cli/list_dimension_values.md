# List Dimension Values

## Purpose
Use this tool to retrieve the actual values for a specific dimension across given metrics. This helps you understand the possible values a dimension can take and is useful for filtering and exploration.

## When to Use
- When you need to see what values are available for a dimension
- When building WHERE clauses and need to know valid dimension values
- When exploring data and want to understand dimension cardinality
- When validating dimension values before using them in queries

## Parameters

### Required Parameters
- **dimension**: The dimension name to retrieve values for (e.g., "region", "product_category")
- **metrics**: List of metrics to use for finding dimension values (e.g., ["revenue", "orders"])

### Optional Parameters
- **start_time**: ISO8601 timestamp for the start of the time range to filter dimension values
- **end_time**: ISO8601 timestamp for the end of the time range to filter dimension values

## Examples

### List Values for a Dimension
```json
{
  "dimension": "region",
  "metrics": ["revenue"]
}
```

### List Dimension Values with Time Filter
```json
{
  "dimension": "product_category",
  "metrics": ["revenue", "order_count"],
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-12-31T23:59:59Z"
}
```

### List Values for Multiple Metrics
```json
{
  "dimension": "customer_segment",
  "metrics": ["revenue", "profit", "customer_count"]
}
```

## Output Format
Returns a tuple of (message, data):
- **message**: JSON string containing execution information
- **data**: Raw text output listing the distinct values for the specified dimension

## Best Practices
1. Always specify both dimension and metrics parameters as they are required
2. Use time filters to get dimension values for specific time periods
3. Consider the metrics you specify as they determine which dimension values are returned
4. This is particularly useful for building dynamic filters and validation
5. Be aware that high-cardinality dimensions may return many values