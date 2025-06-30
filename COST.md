# CodeRipple Cost Analysis

Comprehensive cost breakdown for the CodeRipple serverless analysis pipeline.

## AWS Lambda Costs

### Free Tier Benefits
AWS Lambda provides generous free tier allowances:
- **1 million requests** per month (forever)
- **400,000 GB-seconds** of compute time per month (forever)

### Hermes Lambda (Event Logging)
- **Memory**: 256 MB
- **Typical execution**: 1-2 seconds per event
- **Usage estimate**: 1,000-10,000 events/month
- **Cost**: **FREE** (well within free tier limits)

### Receptionist Lambda (Repository Processing)
- **Memory**: 1GB (1,024 MB) - Updated from 512MB for better performance
- **Ephemeral Storage**: 5GB (5,120 MB) - Testing configuration for 1 week
- **Typical execution**: 30-120 seconds per repository
- **Usage estimate**: 100-1,000 repositories/month

**Cost Analysis:**
- **Moderate usage** (1,000 invocations/month, 60 seconds each):
  - GB-seconds: 60,000
  - **Cost: FREE** (within 400K GB-seconds free tier)
- **Heavy usage** (10,000 invocations/month, 120 seconds each):
  - GB-seconds: 1,200,000
  - Free: 400,000 GB-seconds
  - Paid: 800,000 GB-seconds × $0.0000166667 = **$13.33/month**

### Memory Upgrade Cost Impact
Upgrading Receptionist from 512MB to 1GB:
- **Performance benefit**: 2x CPU allocation, faster git operations
- **Cost impact**: Doubles compute cost but faster execution likely reduces total GB-seconds
- **Net effect**: Minimal cost increase, significant performance gain

## Lambda Ephemeral Storage Costs

### Pricing Structure
- **First 512 MB**: Included in Lambda pricing (no additional cost)
- **Additional storage**: $0.0000000309 per GB-second

### Receptionist 5GB Storage (Testing Phase)
- **Additional storage**: 5GB - 0.5GB = 4.5GB
- **Cost per second**: 4.5GB × $0.0000000309 = $0.000000139 per second

**Weekly cost examples:**
- **Light usage** (100 invocations, 30 seconds each): ~$0.0004
- **Moderate usage** (1,000 invocations, 60 seconds each): ~$0.008
- **Heavy usage** (10,000 invocations, 120 seconds each): ~$0.17

**Total for 1-week testing period**: $0.01-0.20 (negligible)

**Post-testing optimization**: Reduce to 1-2GB based on actual usage patterns to minimize ongoing costs.

## S3 Storage Costs

### Cabinet S3 Bucket (Public Website)
- **Storage class**: Standard
- **Usage**: Event logs, static website files
- **Size estimate**: <1GB for event logs
- **Cost**: ~$0.02/month (minimal)

### Library S3 Bucket (Repository Storage)
- **Storage class**: Standard (with lifecycle policies planned)
- **Usage**: Cloned repositories, analysis files
- **Size estimate**: Varies by repository count and size
- **Cost factors**:
  - Storage: $0.023 per GB/month
  - PUT requests: $0.0005 per 1,000 requests
  - GET requests: $0.0004 per 1,000 requests

**Estimated monthly costs:**
- **Light usage** (10GB storage): ~$0.25/month
- **Moderate usage** (100GB storage): ~$2.50/month
- **Heavy usage** (1TB storage): ~$25/month

## EventBridge Costs

### Custom Events
- **Pricing**: $1.00 per million events
- **Usage estimate**: 1,000-10,000 events/month
- **Cost**: **FREE** (well under 1 million events)

## API Gateway Costs

### REST API (Gatekeeper)
- **Pricing**: $3.50 per million API calls
- **Usage estimate**: 100-1,000 webhook calls/month
- **Cost**: **FREE** (minimal usage)

## Total Monthly Cost Estimates

### Development/Testing Phase
- **Lambda**: FREE (within free tier)
- **S3**: $0.25-2.50 (depending on repository storage)
- **EventBridge**: FREE
- **API Gateway**: FREE
- **Total**: **$0.25-2.50/month**

### Production Phase (Heavy Usage)
- **Lambda**: $13.33 (Receptionist only, others free)
- **S3**: $25 (1TB repository storage)
- **EventBridge**: FREE
- **API Gateway**: FREE
- **Total**: **~$38/month**

## Cost Optimization Strategies

### Immediate (Week 1)
1. **Monitor ephemeral storage usage** - Reduce from 5GB to optimal size
2. **Track repository sizes** - Understand actual storage needs
3. **Monitor Lambda execution times** - Optimize memory allocation

### Short-term (Month 1)
1. **Implement S3 lifecycle policies** - Move old repositories to cheaper storage
2. **Optimize Lambda memory** - Right-size based on performance metrics
3. **Repository cleanup** - Delete processed repositories after analysis

### Long-term (Month 3+)
1. **S3 Intelligent Tiering** - Automatic cost optimization
2. **Lambda Provisioned Concurrency** - If consistent traffic develops
3. **Reserved Capacity** - For predictable workloads

## Cost Monitoring

### CloudWatch Metrics to Track
- Lambda execution duration and memory usage
- S3 storage utilization and request patterns
- EventBridge event volume
- API Gateway request counts

### Alerts to Set Up
- Monthly spend exceeding $50
- S3 storage growth exceeding 500GB
- Lambda execution errors or timeouts

## Conclusion

CodeRipple is designed to be extremely cost-effective:
- **Development phase**: Under $3/month
- **Production phase**: Under $40/month even with heavy usage
- **Free tier benefits**: Significant cost savings for moderate usage
- **Serverless architecture**: Pay only for actual usage, no idle costs

The serverless approach ensures costs scale with usage while maintaining excellent performance and reliability.
