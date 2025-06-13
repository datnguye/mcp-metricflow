# List Entities

## Purpose
Use this tool to retrieve all unique entities available in the semantic model. Entities represent primary keys or identifiers in your data model (e.g., user_id, order_id, product_id).

## When to Use
- When you need to discover what entities are available in the semantic model
- When you want to see entities that are common across specific metrics
- When building queries and need to understand entity relationships
- When you need to identify primary keys for joining data

## Parameters

### Required Parameters
None - all parameters are optional

### Optional Parameters
- **metrics**: List of metrics to find common entities for (e.g., ["revenue", "orders"])

## Examples

### List All Entities
```json
{}
```

### List Entities for Specific Metrics
```json
{
  "metrics": ["revenue", "order_count"]
}
```

## Output Format
Returns a tuple of (message, data):
- **message**: JSON string containing execution information
- **data**: Raw text output listing available entities

## Best Practices
1. Use without metrics to see all available entities in the semantic model
2. Use with metrics to find entities that are common to those specific metrics
3. Entities are useful for understanding data granularity and join relationships
4. Consider entities when planning metric queries that need specific grouping levels