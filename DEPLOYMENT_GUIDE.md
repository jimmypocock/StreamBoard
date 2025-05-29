# StreamBoard AWS Deployment Guide


This guide provides comprehensive insights for deploying StreamBoard to AWS using CDK, including architecture recommendations, cost analysis, and best practices.

## 🏗️ Recommended Architecture: ECS Fargate


### Why ECS Fargate is Best for StreamBoard


#### Streamlit Requirements

- **Persistent WebSocket connections** - Required for real-time dashboard updates
- **In-memory caching** - Leverages `st.cache_data` for performance
- **Long-running processes** - Maintains session state across user interactions
- **Not suitable for Lambda** - WebSocket timeouts and session state requirements

#### Key Advantages

- No server management overhead
- Automatic scaling capabilities
- Built-in load balancing with ALB
- Zero-downtime deployments
- Cost-effective for steady traffic patterns

## 📦 AWS Resources Architecture


### Core Infrastructure Components


```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFront                           │
│                     (Optional CDN)                          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Application Load Balancer                    │
│                    (with SSL/TLS)                           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    ECS Fargate Service                      │
│              ┌──────────────┐  ┌──────────────┐             │
│              │   Task 1     │  │   Task 2     │             │
│              │ StreamBoard  │  │ StreamBoard  │             │
│              └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Supporting Services                     │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────┐      │
│  │  Secrets   │  │ CloudWatch │  │  ElastiCache      │      │
│  │  Manager   │  │    Logs    │  │  Redis (Optional) │      │
│  └────────────┘  └────────────┘  └───────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Required AWS Services


1. **Networking**
   - VPC with public/private subnets
   - NAT Gateway or VPC Endpoints
   - Security Groups

2. **Compute**
   - ECS Cluster
   - Fargate Service
   - Task Definitions

3. **Storage & Registry**
   - ECR for Docker images
   - S3 bucket (optional for assets)

4. **Load Balancing & DNS**
   - Application Load Balancer
   - Target Groups with health checks
   - Route 53 (optional for custom domain)
   - ACM for SSL certificates

5. **Security & Secrets**
   - Secrets Manager for API credentials
   - IAM roles and policies
   - Security Groups

6. **Monitoring & Logging**
   - CloudWatch Logs
   - CloudWatch Metrics
   - CloudWatch Alarms

7. **Caching (Optional)**
   - ElastiCache Redis for shared cache

## 💰 Cost Analysis


### Small Production Setup (1-10 concurrent users)


| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| ECS Fargate | 0.25 vCPU, 0.5GB RAM | $20-30 |
| Application Load Balancer | Basic | $20 |
| NAT Gateway | Single AZ | $45 |
| Data Transfer | ~50GB | $5-10 |
| Secrets Manager | 5 secrets | $2 |
| CloudWatch | Logs & Metrics | $5 |
| **Total** | | **$97-112/month** |

### Medium Setup (10-50 concurrent users)


| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| ECS Fargate | 0.5 vCPU, 1GB RAM x 2 tasks | $80-120 |
| Application Load Balancer | With rules | $22 |
| NAT Gateway | Multi-AZ | $90 |
| ElastiCache Redis | cache.t3.micro | $25 |
| Data Transfer | ~200GB | $20 |
| Other Services | Logs, Secrets, etc. | $15 |
| **Total** | | **$252-292/month** |

### Large Setup (50+ concurrent users)


| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| ECS Fargate | 1 vCPU, 2GB RAM x 4 tasks | $320-400 |
| Application Load Balancer | With WAF | $45 |
| NAT Gateway | Multi-AZ | $90 |
| ElastiCache Redis | cache.m5.large | $120 |
| CloudFront | Global CDN | $50 |
| Other Services | Enhanced monitoring | $30 |
| **Total** | | **$655-735/month** |

## 🔄 Alternative Architectures


### AWS App Runner (Simpler but Less Control)

- **Pros**: Easier deployment, automatic scaling, built-in CI/CD
- **Cons**: Less configuration options, newer service
- **Cost**: ~$50-80/month for small workloads
- **Best for**: Quick deployments, less DevOps overhead

### EC2 with Auto Scaling (More Control)

- **Pros**: Full control, potentially cheaper, custom configurations
- **Cons**: More management overhead, need to handle updates
- **Cost**: ~$30-50/month (t3.small reserved instance)
- **Best for**: Teams with strong DevOps capabilities

### Lightsail Container Service (Simplest)

- **Pros**: Fixed pricing, very simple, includes everything
- **Cons**: Limited scaling, less flexibility
- **Cost**: $40/month (Micro container)
- **Best for**: Small teams, predictable traffic

## 🛠️ CDK Stack Structure


### Recommended CDK Organization


```typescript
streamboard-cdk/
├── bin/
│   └── streamboard.ts          // CDK app entry point
├── lib/
│   ├── stacks/
│   │   ├── vpc-stack.ts        // Network infrastructure
│   │   ├── security-stack.ts   // Secrets, IAM roles
│   │   ├── container-stack.ts  // ECS, Fargate, ECR
│   │   ├── network-stack.ts    // ALB, Route53
│   │   └── monitoring-stack.ts // CloudWatch, alarms
│   └── constructs/
│       ├── fargate-service.ts  // Reusable Fargate construct
│       └── alb-config.ts       // ALB configuration
└── config/
    ├── dev.json               // Development config
    └── prod.json              // Production config
```

### Key CDK Components


```typescript
// 1. VPC Stack
- Public subnets for ALB
- Private subnets for Fargate
- VPC Endpoints to reduce costs

// 2. Security Stack
- Secrets Manager for credentials
- IAM roles with least privilege
- Security groups with minimal ports

// 3. Container Stack
- ECR repository with lifecycle rules
- Task definition with proper CPU/memory
- Service with auto-scaling policies

// 4. Network Stack
- ALB with sticky sessions
- HTTPS listeners with ACM cert
- Health check configuration

// 5. Monitoring Stack
- Log groups with retention
- CPU/Memory alarms
- Custom metrics dashboard
```

## 🎯 Production Best Practices


### Cost Optimization


1. **Use Fargate Spot**
   - 70% discount for interruptible workloads
   - Good for development environments
   - Mix with on-demand for production

2. **VPC Endpoints instead of NAT**
   - Save $45/month per NAT gateway
   - Use for S3, Secrets Manager, ECR

3. **Auto-scaling Configuration**
   ```typescript
   // Scale down during off-hours
   scheduleScaling: {
     minCapacity: 0,  // Nights/weekends
     maxCapacity: 4,  // Business hours
   }
   ```

4. **Reserved Capacity**
   - Compute Savings Plans for 1-3 year commitment
   - Up to 50% discount on Fargate

### Performance Optimization


1. **Container Configuration**
   ```dockerfile
   # Multi-stage build for smaller images
   FROM python:3.9-slim as builder
   # ... build steps

   FROM python:3.9-slim
   # Only copy necessary files
   ```

2. **Caching Strategy**
   - Use ElastiCache Redis for shared state
   - CloudFront for static assets
   - Proper cache headers

3. **Health Checks**
   ```python
   # Add health endpoint in app.py
   @app.route('/health')
   def health():
       return {"status": "healthy"}
   ```

### Security Hardening


1. **Secrets Management**
   ```typescript
   // Never hardcode credentials
   taskDefinition.addContainer('streamboard', {
     secrets: {
       GA_CREDENTIALS: ecs.Secret.fromSecretsManager(gaSecret),
       AWS_CREDENTIALS: ecs.Secret.fromSecretsManager(awsSecret),
     }
   });
   ```

2. **Network Security**
   - Private subnets for containers
   - WAF rules on ALB
   - VPC Flow Logs enabled

3. **Container Security**
   - Non-root user in Dockerfile
   - Read-only root filesystem
   - Security scanning in ECR

### Monitoring & Alerting


1. **Essential Metrics**
   - Task CPU/Memory utilization
   - ALB response times
   - Error rates
   - Active connections

2. **Recommended Alarms**
   - High CPU (>80% for 5 minutes)
   - High memory (>90%)
   - ALB unhealthy hosts
   - 5xx error rate

## 🚀 Deployment Strategy


### Blue/Green Deployment

```typescript
service: {
  deploymentController: {
    type: ecs.DeploymentControllerType.ECS,
  },
  desiredCount: 2,
  deploymentConfiguration: {
    maximumPercent: 200,      // Allow doubling during deploy
    minimumHealthyPercent: 100, // Keep all healthy during deploy
  }
}
```

### CI/CD Pipeline

1. GitHub Actions builds Docker image
2. Push to ECR
3. Update ECS service
4. Automatic rollback on failures

## 📊 Scaling Considerations


### Horizontal Scaling

- Multiple Fargate tasks behind ALB
- Sticky sessions required for Streamlit
- Session affinity on ALB (1 hour)

### Vertical Scaling

- Start with 0.25 vCPU, 0.5GB RAM
- Monitor and adjust based on usage
- Fargate supports up to 4 vCPU, 30GB RAM

### Shared State

- Use Redis for cache sharing
- Store sessions in Redis
- Enables true horizontal scaling

## 💡 Why Not Serverless?


While Lambda is great for many use cases, Streamlit requires:

1. **Persistent Connections**
   - WebSocket connections for real-time updates
   - Lambda has 15-minute maximum timeout
   - API Gateway WebSocket has 2-hour limit

2. **Session State**
   - Streamlit maintains user session in memory
   - Lambda loses state between invocations
   - Cold starts would reset user sessions

3. **Caching Benefits**
   - In-memory caching significantly improves performance
   - Lambda would lose cache on every cold start
   - Fargate maintains cache between requests

## 🎬 Getting Started


1. **Containerize Application**
   ```bash
   docker build -t streamboard .
   docker run -p 8501:8501 streamboard
   ```

2. **Deploy with CDK**
   ```bash
   npm install -g aws-cdk
   cdk init app --language typescript
   cdk deploy StreamBoardStack
   ```

3. **Monitor & Optimize**
   - Watch CloudWatch metrics
   - Adjust container size based on usage
   - Enable auto-scaling when patterns emerge

## 📈 Expected Performance


- **Response Time**: <500ms for cached data
- **Concurrent Users**: 50-100 per container
- **Uptime**: 99.9% with multi-AZ setup
- **Deployment Time**: 5-10 minutes for updates

This architecture provides a robust, scalable foundation for StreamBoard while keeping costs reasonable and management overhead low.