# List Dimensions

## Purpose
Use this tool to retrieve all unique dimensions available in the semantic model.

## When to Use
- When you need to discover available dimensions for grouping data
- When you want to see dimensions shared across specific metrics
- When building queries and need to know dimension options

## Parameters

### Required Parameters
None - all parameters are optional

### Optional Parameters
- **metrics**: List of metrics to find common dimensions for (e.g., ["revenue", "orders"])

## Examples

### List All Dimensions
```json
{}
```

### List Dimensions for Specific Metrics
```json
{
  "metrics": ["revenue", "order_count"]
}
```

## Output Format
Returns a tuple of (message, data):
- **message**: JSON string containing execution information
- **data**: Raw text output listing available dimensions

## Best Practices
1. Use without metrics to see all available dimensions
2. Use with metrics to find dimensions common to those specific metrics
3. Useful for understanding what groupings are possible in queries