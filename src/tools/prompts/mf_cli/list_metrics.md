# List Metrics

## Purpose
Use this tool to retrieve metadata about available metrics and their associated dimensions.

## When to Use
- When you need to discover what metrics are available in the semantic model
- When you want to see which dimensions are available for specific metrics
- When searching for metrics by name or keyword

## Parameters

### Required Parameters
None - all parameters are optional

### Optional Parameters
- **search**: Filter metrics by search term (e.g., "revenue", "user")
- **show_all_dimensions**: Show all dimensions for each metric (default: false, shows truncated list)

## Examples

### List All Metrics
```json
{}
```

### Search for Specific Metrics
```json
{
  "search": "revenue"
}
```

### Show All Dimensions for Metrics
```json
{
  "show_all_dimensions": true
}
```

## Output Format
Returns a tuple of (message, data):
- **message**: JSON string containing execution information
- **data**: Raw text output showing metrics and their dimensions

## Best Practices
1. Use search to filter when you have many metrics
2. Use show_all_dimensions when you need complete dimension information
3. This is useful for metric discovery and understanding data model structure