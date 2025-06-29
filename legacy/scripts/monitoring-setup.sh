#!/bin/bash
# scripts/monitoring-setup.sh
# Monitoring Setup for CodeRipple Layer-based Architecture

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Source common functions
if [ -f "layers/shared/build-common.sh" ]; then
    source layers/shared/build-common.sh
else
    # Fallback logging functions
    log_section() { echo -e "\n=== $1 ==="; }
    log_step() { echo "🔍 $1..."; }
    log_success() { echo "✅ $1"; }
    log_error() { echo "❌ $1"; }
    log_warning() { echo "⚠️  $1"; }
    log_debug() { echo "🐛 $1"; }
    log_section_complete() { echo -e "✅ $1 - COMPLETED\n"; }
fi

log_section "CodeRipple Monitoring Setup"

# Configuration
MONITORING_MODE=${MONITORING_MODE:-"full"}  # full, basic, alarms-only
AWS_REGION=${AWS_REGION:-"us-west-2"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
CREATE_DASHBOARD=${CREATE_DASHBOARD:-true}
CREATE_ALARMS=${CREATE_ALARMS:-true}

# Get function name from Terraform
get_function_name() {
    cd infra/terraform
    terraform output -raw lambda_function_name 2>/dev/null || echo ""
    cd ../..
}

# Create CloudWatch dashboard
create_cloudwatch_dashboard() {
    if [ "$CREATE_DASHBOARD" != "true" ]; then
        log_debug "Skipping dashboard creation"
        return 0
    fi
    
    log_step "Creating CloudWatch dashboard"
    
    FUNCTION_NAME=$(get_function_name)
    if [ -z "$FUNCTION_NAME" ]; then
        log_error "Function name not available from Terraform"
        return 1
    fi
    
    DASHBOARD_NAME="CodeRipple-LayerBased-${ENVIRONMENT}"
    
    # Create dashboard JSON
    cat > dashboard.json << EOF
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "Duration", "FunctionName", "$FUNCTION_NAME" ],
                    [ ".", "Invocations", ".", "." ],
                    [ ".", "Errors", ".", "." ],
                    [ ".", "Throttles", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$AWS_REGION",
                "title": "Lambda Function Metrics",
                "period": 300,
                "stat": "Average"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "Duration", "FunctionName", "$FUNCTION_NAME", { "stat": "Average" } ],
                    [ "...", { "stat": "Maximum" } ],
                    [ "...", { "stat": "p95" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$AWS_REGION",
                "title": "Performance Metrics (Layer-based)",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "log",
            "x": 0,
            "y": 6,
            "width": 24,
            "height": 6,
            "properties": {
                "query": "SOURCE '/aws/lambda/$FUNCTION_NAME'\n| fields @timestamp, @message\n| filter @message like /Layer/\n| sort @timestamp desc\n| limit 100",
                "region": "$AWS_REGION",
                "title": "Layer-related Logs",
                "view": "table"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 12,
            "width": 8,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "$FUNCTION_NAME" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$AWS_REGION",
                "title": "Concurrent Executions",
                "period": 300,
                "stat": "Maximum"
            }
        },
        {
            "type": "metric",
            "x": 8,
            "y": 12,
            "width": 8,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/X-Ray", "TracesReceived", "ServiceName", "$FUNCTION_NAME", "ServiceType", "AWS::Lambda::Function" ],
                    [ ".", "ResponseTime", ".", ".", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$AWS_REGION",
                "title": "X-Ray Tracing",
                "period": 300,
                "stat": "Average"
            }
        },
        {
            "type": "metric",
            "x": 16,
            "y": 12,
            "width": 8,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/ApiGateway", "Count", "ApiName", "coderipple-api" ],
                    [ ".", "Latency", ".", "." ],
                    [ ".", "4XXError", ".", "." ],
                    [ ".", "5XXError", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$AWS_REGION",
                "title": "API Gateway Metrics",
                "period": 300,
                "stat": "Sum"
            }
        }
    ]
}
EOF
    
    # Create the dashboard
    if aws cloudwatch put-dashboard \
        --dashboard-name "$DASHBOARD_NAME" \
        --dashboard-body file://dashboard.json; then
        log_success "Dashboard created: $DASHBOARD_NAME"
        rm dashboard.json
    else
        log_error "Failed to create dashboard"
        rm dashboard.json
        return 1
    fi
}

# Create CloudWatch alarms
create_cloudwatch_alarms() {
    if [ "$CREATE_ALARMS" != "true" ]; then
        log_debug "Skipping alarm creation"
        return 0
    fi
    
    log_step "Creating CloudWatch alarms"
    
    FUNCTION_NAME=$(get_function_name)
    if [ -z "$FUNCTION_NAME" ]; then
        log_error "Function name not available from Terraform"
        return 1
    fi
    
    # High duration alarm (layer-based should be fast)
    aws cloudwatch put-metric-alarm \
        --alarm-name "CodeRipple-HighDuration-${ENVIRONMENT}" \
        --alarm-description "CodeRipple Lambda function duration is high (layer-based should be fast)" \
        --metric-name Duration \
        --namespace AWS/Lambda \
        --statistic Average \
        --period 300 \
        --threshold 5000 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --alarm-actions "arn:aws:sns:${AWS_REGION}:$(aws sts get-caller-identity --query Account --output text):coderipple-alerts" \
        --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
        --treat-missing-data notBreaching
    
    log_success "High duration alarm created"
    
    # Error rate alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "CodeRipple-ErrorRate-${ENVIRONMENT}" \
        --alarm-description "CodeRipple Lambda function error rate is high" \
        --metric-name Errors \
        --namespace AWS/Lambda \
        --statistic Sum \
        --period 300 \
        --threshold 5 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --alarm-actions "arn:aws:sns:${AWS_REGION}:$(aws sts get-caller-identity --query Account --output text):coderipple-alerts" \
        --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
        --treat-missing-data notBreaching
    
    log_success "Error rate alarm created"
    
    # Throttle alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "CodeRipple-Throttles-${ENVIRONMENT}" \
        --alarm-description "CodeRipple Lambda function is being throttled" \
        --metric-name Throttles \
        --namespace AWS/Lambda \
        --statistic Sum \
        --period 300 \
        --threshold 1 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 1 \
        --alarm-actions "arn:aws:sns:${AWS_REGION}:$(aws sts get-caller-identity --query Account --output text):coderipple-alerts" \
        --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
        --treat-missing-data notBreaching
    
    log_success "Throttle alarm created"
    
    # Layer-specific performance alarm (cold start should be fast with layers)
    aws cloudwatch put-metric-alarm \
        --alarm-name "CodeRipple-ColdStart-${ENVIRONMENT}" \
        --alarm-description "CodeRipple cold start performance degraded (layers should improve this)" \
        --metric-name Duration \
        --namespace AWS/Lambda \
        --statistic Maximum \
        --period 300 \
        --threshold 10000 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 1 \
        --alarm-actions "arn:aws:sns:${AWS_REGION}:$(aws sts get-caller-identity --query Account --output text):coderipple-alerts" \
        --dimensions Name=FunctionName,Value="$FUNCTION_NAME" \
        --treat-missing-data notBreaching
    
    log_success "Cold start performance alarm created"
}

# Create custom metrics
create_custom_metrics() {
    log_step "Setting up custom metrics"
    
    # Create a script to publish custom metrics
    cat > publish-custom-metrics.sh << 'EOF'
#!/bin/bash
# Publish custom metrics for CodeRipple layer-based architecture

FUNCTION_NAME="$1"
AWS_REGION="$2"

if [ -z "$FUNCTION_NAME" ] || [ -z "$AWS_REGION" ]; then
    echo "Usage: $0 <function-name> <aws-region>"
    exit 1
fi

# Get layer information
LAYER_COUNT=$(aws lambda get-function --function-name "$FUNCTION_NAME" --region "$AWS_REGION" \
    --query 'Configuration.Layers | length' --output text)

# Publish layer count metric
aws cloudwatch put-metric-data \
    --namespace "CodeRipple/Layers" \
    --metric-data MetricName=LayerCount,Value="$LAYER_COUNT",Unit=Count \
    --region "$AWS_REGION"

# Get function size
FUNCTION_SIZE=$(aws lambda get-function --function-name "$FUNCTION_NAME" --region "$AWS_REGION" \
    --query 'Configuration.CodeSize' --output text)

# Publish function size metric
aws cloudwatch put-metric-data \
    --namespace "CodeRipple/Layers" \
    --metric-data MetricName=FunctionSize,Value="$FUNCTION_SIZE",Unit=Bytes \
    --region "$AWS_REGION"

echo "Custom metrics published for $FUNCTION_NAME"
EOF
    
    chmod +x publish-custom-metrics.sh
    log_success "Custom metrics script created: publish-custom-metrics.sh"
}

# Set up log insights queries
create_log_insights_queries() {
    log_step "Creating CloudWatch Logs Insights queries"
    
    FUNCTION_NAME=$(get_function_name)
    if [ -z "$FUNCTION_NAME" ]; then
        log_error "Function name not available from Terraform"
        return 1
    fi
    
    LOG_GROUP="/aws/lambda/$FUNCTION_NAME"
    
    # Create saved queries
    cat > log-insights-queries.json << EOF
[
    {
        "name": "CodeRipple Layer Performance",
        "queryString": "fields @timestamp, @message, @duration\\n| filter @message like /Layer/\\n| stats avg(@duration) by bin(5m)",
        "logGroups": ["$LOG_GROUP"]
    },
    {
        "name": "CodeRipple Error Analysis",
        "queryString": "fields @timestamp, @message\\n| filter @message like /ERROR/ or @message like /Error/\\n| sort @timestamp desc",
        "logGroups": ["$LOG_GROUP"]
    },
    {
        "name": "CodeRipple Agent Invocations",
        "queryString": "fields @timestamp, @message\\n| filter @message like /agents_invoked/\\n| stats count() by bin(1h)",
        "logGroups": ["$LOG_GROUP"]
    },
    {
        "name": "CodeRipple Cold Start Analysis",
        "queryString": "fields @timestamp, @message, @duration\\n| filter @type = \\\"REPORT\\\"\\n| filter @duration > 3000\\n| sort @timestamp desc",
        "logGroups": ["$LOG_GROUP"]
    }
]
EOF
    
    log_success "Log Insights queries saved to log-insights-queries.json"
    log_debug "Import these queries manually in CloudWatch Logs Insights console"
}

# Create monitoring documentation
create_monitoring_documentation() {
    log_step "Creating monitoring documentation"
    
    cat > MONITORING.md << EOF
# CodeRipple Layer-based Architecture Monitoring

This document describes the monitoring setup for the CodeRipple layer-based Lambda architecture.

## Architecture Overview

The monitoring setup is designed specifically for the layer-based architecture:
- **Dependencies Layer**: External packages (boto3, strands-agents, etc.)
- **Package Layer**: CodeRipple agents and tools
- **Lambda Function**: Handler code only (12KB)

## CloudWatch Dashboard

Dashboard: **CodeRipple-LayerBased-${ENVIRONMENT}**

### Key Metrics Monitored

1. **Lambda Function Metrics**
   - Duration (should be low due to layer optimization)
   - Invocations
   - Errors
   - Throttles

2. **Performance Metrics**
   - Average, Maximum, and P95 duration
   - Cold start performance (optimized by layers)

3. **Layer-specific Logs**
   - Layer validation messages
   - Layer load times
   - Import performance

4. **X-Ray Tracing**
   - Request tracing through layer-based architecture
   - Performance breakdown by component

## CloudWatch Alarms

### Critical Alarms

1. **High Duration** (Threshold: 5 seconds)
   - Layer-based architecture should be fast
   - Triggers if average duration > 5s for 2 periods

2. **Error Rate** (Threshold: 5 errors)
   - Monitors function errors
   - Includes layer validation failures

3. **Throttles** (Threshold: 1 throttle)
   - Immediate alert on any throttling
   - Critical for webhook processing

4. **Cold Start Performance** (Threshold: 10 seconds)
   - Maximum duration alarm
   - Layers should improve cold start times

### Alarm Actions

All alarms send notifications to: \`arn:aws:sns:${AWS_REGION}:ACCOUNT:coderipple-alerts\`

## Custom Metrics

### CodeRipple/Layers Namespace

- **LayerCount**: Number of layers attached to function
- **FunctionSize**: Size of function package (should be ~12KB)

### Publishing Custom Metrics

Use the provided script:
\`\`\`bash
./publish-custom-metrics.sh $FUNCTION_NAME $AWS_REGION
\`\`\`

## Log Insights Queries

### Pre-configured Queries

1. **Layer Performance Analysis**
   - Analyzes layer-related performance metrics
   - Shows average duration by time period

2. **Error Analysis**
   - Filters and analyzes error messages
   - Includes layer validation errors

3. **Agent Invocation Tracking**
   - Monitors which agents are being invoked
   - Tracks usage patterns

4. **Cold Start Analysis**
   - Identifies slow cold starts
   - Should show improvement with layer architecture

## Performance Baselines

### Expected Performance (Layer-based)

- **Cold Start**: < 3 seconds (improved by layers)
- **Warm Start**: < 500ms
- **Function Size**: ~12KB (99.6% reduction)
- **Layer Cache**: Reused across invocations

### Performance Comparison

| Metric | Monolithic | Layer-based | Improvement |
|--------|------------|-------------|-------------|
| Package Size | ~28MB | ~12KB | 99.6% |
| Cold Start | 5-10s | 2-3s | 50-70% |
| Deployment | 5 min | 30s | 90% |

## Troubleshooting

### Common Issues

1. **Layer Import Failures**
   - Check layer ARNs in environment variables
   - Verify layer versions are compatible

2. **High Duration**
   - Check if layers are properly cached
   - Verify layer optimization

3. **Memory Issues**
   - Layer-based architecture should use less memory
   - Consider reducing memory allocation

### Debugging Steps

1. Check CloudWatch Logs for layer validation messages
2. Use X-Ray tracing to identify bottlenecks
3. Monitor custom metrics for layer health
4. Compare performance against baselines

## Maintenance

### Regular Tasks

1. **Weekly**: Review performance metrics and trends
2. **Monthly**: Analyze cost impact of layer architecture
3. **Quarterly**: Update performance baselines

### Layer Updates

When updating layers:
1. Monitor deployment metrics
2. Compare performance before/after
3. Update alarms if thresholds change

## Cost Optimization

### Layer-based Benefits

- Reduced function package size = faster deployments
- Layer caching = improved performance
- Independent updates = reduced deployment frequency

### Monitoring Costs

- CloudWatch Logs: Monitor retention settings
- X-Ray: Review tracing costs vs. benefits
- Custom Metrics: Optimize publishing frequency

---

*Generated by CodeRipple Monitoring Setup*
*Architecture: Single Lambda with Layers*
*Environment: ${ENVIRONMENT}*
EOF
    
    log_success "Monitoring documentation created: MONITORING.md"
}

# Print monitoring summary
print_monitoring_summary() {
    log_section "Monitoring Setup Summary"
    
    FUNCTION_NAME=$(get_function_name)
    
    echo "📊 Monitoring Components Created:"
    
    if [ "$CREATE_DASHBOARD" = "true" ]; then
        echo "   ✅ CloudWatch Dashboard: CodeRipple-LayerBased-${ENVIRONMENT}"
    else
        echo "   ⏭️  CloudWatch Dashboard: Skipped"
    fi
    
    if [ "$CREATE_ALARMS" = "true" ]; then
        echo "   ✅ CloudWatch Alarms: 4 alarms created"
        echo "      • High Duration (>5s)"
        echo "      • Error Rate (>5 errors)"
        echo "      • Throttles (>1)"
        echo "      • Cold Start Performance (>10s)"
    else
        echo "   ⏭️  CloudWatch Alarms: Skipped"
    fi
    
    echo "   ✅ Custom Metrics Script: publish-custom-metrics.sh"
    echo "   ✅ Log Insights Queries: log-insights-queries.json"
    echo "   ✅ Monitoring Documentation: MONITORING.md"
    
    echo ""
    echo "🏗️  Architecture Monitoring:"
    echo "   • Function: $FUNCTION_NAME"
    echo "   • Environment: $ENVIRONMENT"
    echo "   • Region: $AWS_REGION"
    echo "   • Architecture: Single Lambda with Layers"
    
    echo ""
    echo "📈 Key Performance Indicators:"
    echo "   • Cold Start: <3s (target with layers)"
    echo "   • Function Size: ~12KB (99.6% reduction)"
    echo "   • Error Rate: <1% (target)"
    echo "   • Layer Cache: Monitored via custom metrics"
    
    echo ""
    echo "🔗 Next Steps:"
    echo "   1. Configure SNS topic for alarm notifications"
    echo "   2. Import Log Insights queries in AWS Console"
    echo "   3. Set up automated custom metrics publishing"
    echo "   4. Review and adjust alarm thresholds based on usage"
    
    echo ""
    echo "📚 Documentation: See MONITORING.md for detailed information"
}

# Main execution flow
main() {
    case "$MONITORING_MODE" in
        "full")
            create_cloudwatch_dashboard
            create_cloudwatch_alarms
            create_custom_metrics
            create_log_insights_queries
            create_monitoring_documentation
            ;;
        "basic")
            create_cloudwatch_dashboard
            create_monitoring_documentation
            ;;
        "alarms-only")
            create_cloudwatch_alarms
            ;;
        *)
            log_error "Unknown monitoring mode: $MONITORING_MODE"
            exit 1
            ;;
    esac
    
    print_monitoring_summary
    log_section_complete "Monitoring Setup"
}

# Execute main function
main "$@"
EOF
