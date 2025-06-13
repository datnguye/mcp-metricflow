# Validate Configurations

## Purpose
Use this tool to perform validations against the defined model configurations to ensure they are correct and functional.

## When to Use
- Before deploying changes to production
- When troubleshooting configuration issues
- As part of CI/CD pipeline validation
- When developing new semantic models

## Parameters

### Required Parameters
None - all parameters are optional

### Optional Parameters
- **dw_timeout**: Timeout in seconds for data warehouse validation steps
- **skip_dw**: Skip data warehouse validations (default: false)
- **show_all**: Show warnings and future errors (default: false)
- **verbose_issues**: Show extra details for any issues (default: false)
- **semantic_validation_workers**: Number of workers for semantic validations (for large configs)

## Examples

### Basic Validation
```json
{}
```

### Skip Data Warehouse Validation
```json
{
  "skip_dw": true
}
```

### Verbose Validation with All Details
```json
{
  "show_all": true,
  "verbose_issues": true
}
```

### Validation with Custom Timeout
```json
{
  "dw_timeout": 300,
  "show_all": true
}
```

## Output Format
Returns a tuple of (message, data):
- **message**: JSON string containing execution information
- **data**: Raw text output showing validation results, errors, and warnings

## Best Practices
1. Run basic validation regularly during development
2. Use skip_dw for faster validation when data warehouse is unavailable
3. Use verbose_issues when debugging specific configuration problems
4. Set appropriate timeout values for large data warehouses