# Health Checks

## Purpose
Use this tool to perform comprehensive health checks against the data warehouse and MetricFlow semantic model. This validates that the connection is working and the semantic model is properly configured.

## When to Use
- When you want to verify that MetricFlow can connect to the data warehouse
- When troubleshooting connectivity or configuration issues
- When validating that the semantic model is properly set up
- When performing routine system health monitoring
- After making changes to the semantic model configuration

## Parameters

### Required Parameters
None - this tool takes no parameters

### Optional Parameters
None - health checks run a standard set of validation tests

## Examples

### Run Health Checks
```json
{}
```

## Output Format
Returns a tuple of (message, data):
- **message**: JSON string containing execution information and health check status
- **data**: Raw text output showing detailed health check results

## Health Check Components
The health checks typically validate:
1. **Database Connectivity**: Verifies connection to the data warehouse
2. **Semantic Model Validation**: Checks that the semantic model is properly configured
3. **Table Accessibility**: Ensures that referenced tables and views are accessible
4. **Metric Definitions**: Validates that metric definitions are syntactically correct
5. **Dimension Relationships**: Checks that dimension joins are properly configured

## Best Practices
1. Run health checks after any configuration changes
2. Use this as a first step when troubleshooting query issues
3. Health checks help identify configuration problems before running complex queries
4. Regular health checks can help catch data warehouse connectivity issues early
5. Review the detailed output to understand any specific issues found