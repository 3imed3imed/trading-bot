# Emergent AI Builder - Knowledge Base

## What is emergent.sh?

emergent.sh is an AI-powered platform that helps developers build full-stack applications quickly. It understands natural language requirements and generates complete, working applications with:

- Frontend interfaces
- Backend APIs
- Database schemas
- Authentication systems
- Deployment configurations

## Key Principles

### 1. Rapid Development
Generate working prototypes in minutes rather than hours or days.

### 2. Best Practices by Default
Every generated application follows industry best practices:
- Clean code architecture
- Secure by default
- Well-documented
- Easy to extend

### 3. Technology Agnostic
Support for multiple tech stacks to match project needs:
- Choose the right tool for the job
- No lock-in to specific frameworks
- Easy migration between technologies

### 4. Production Ready
Generated code should be:
- Scalable
- Maintainable
- Testable
- Deployable

## Common Use Cases

### Web Applications

#### Single Page Applications (SPAs)
- React + TypeScript
- Vue.js + Composition API
- Angular with standalone components

#### Server-Side Rendered (SSR)
- Next.js for React
- Nuxt.js for Vue
- SvelteKit

#### Progressive Web Apps (PWAs)
- Service workers
- Offline capability
- Push notifications

### API Development

#### REST APIs
- Express.js (Node.js)
- FastAPI (Python)
- Gin (Go)
- Spring Boot (Java)

#### GraphQL APIs
- Apollo Server
- Hasura
- Prisma

#### Real-time APIs
- WebSockets
- Server-Sent Events
- Socket.io

### Data & Backend

#### Database Design
- Relational: PostgreSQL, MySQL
- NoSQL: MongoDB, Redis
- Cloud: Firebase, Supabase

#### Authentication
- JWT tokens
- OAuth 2.0
- Session-based
- Multi-factor authentication

#### File Storage
- Local filesystem
- S3-compatible storage
- CDN integration

## Architecture Patterns

### Monolithic
Best for:
- Small to medium applications
- Tight coupling acceptable
- Simple deployment

Structure:
```
app/
  ├── frontend/
  ├── backend/
  ├── database/
  └── config/
```

### Microservices
Best for:
- Large, complex applications
- Team scalability
- Independent deployment

Structure:
```
services/
  ├── auth-service/
  ├── user-service/
  ├── api-gateway/
  └── shared/
```

### Serverless
Best for:
- Event-driven workloads
- Variable traffic
- Cost optimization

Structure:
```
functions/
  ├── api/
  ├── workers/
  └── triggers/
```

## Tech Stack Recommendations

### Startup MVP
- Frontend: React + Vite
- Backend: Node.js + Express
- Database: PostgreSQL
- Auth: JWT
- Deploy: Vercel/Railway

**Why**: Fast development, low cost, easy scaling

### Enterprise Application
- Frontend: Next.js + TypeScript
- Backend: NestJS
- Database: PostgreSQL + Redis
- Auth: OAuth 2.0
- Deploy: Kubernetes

**Why**: Type safety, scalability, maintainability

### Real-time Application
- Frontend: React + WebSocket
- Backend: Node.js + Socket.io
- Database: MongoDB + Redis
- Auth: JWT
- Deploy: AWS/GCP

**Why**: Low latency, real-time updates

### Data-Intensive Application
- Frontend: React + D3.js
- Backend: Python + FastAPI
- Database: PostgreSQL + Timescale
- Queue: Celery + Redis
- Deploy: Docker + AWS

**Why**: Data processing, analytics, visualization

## Security Best Practices

### Input Validation
```javascript
// Always validate and sanitize
const validateEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};
```

### SQL Injection Prevention
```javascript
// Use parameterized queries
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);
```

### Authentication
```javascript
// Use bcrypt for passwords
const hashedPassword = await bcrypt.hash(password, 10);

// Verify with constant-time comparison
const isValid = await bcrypt.compare(password, hashedPassword);
```

### CORS Configuration
```javascript
// Restrict origins in production
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true
}));
```

## Performance Optimization

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Caching strategies

### Backend
- Database indexing
- Query optimization
- Connection pooling
- Caching (Redis)

### Database
- Proper indexes
- Query optimization
- Partitioning
- Replication

## Testing Strategies

### Unit Tests
Test individual functions and components in isolation.

### Integration Tests
Test how different parts work together.

### End-to-End Tests
Test complete user workflows.

### Load Tests
Test performance under heavy load.

## Deployment Options

### Platform as a Service (PaaS)
- Vercel (frontend)
- Railway (full-stack)
- Heroku (legacy)
- Render (full-stack)

### Infrastructure as a Service (IaaS)
- AWS (EC2, ECS, Lambda)
- Google Cloud Platform
- Microsoft Azure
- DigitalOcean

### Container Orchestration
- Kubernetes
- Docker Swarm
- AWS ECS
- Google Kubernetes Engine

## Common Patterns

### API Design
- RESTful conventions
- Versioning (v1, v2)
- Pagination
- Filtering and sorting
- Error handling

### Error Handling
```javascript
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
  }
}
```

### Configuration Management
```javascript
// Use environment variables
const config = {
  port: process.env.PORT || 3000,
  database: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET
};
```

### Logging
```javascript
// Structured logging
logger.info('User logged in', {
  userId: user.id,
  timestamp: new Date(),
  ip: req.ip
});
```

## Resources

### Documentation
- MDN Web Docs
- Node.js Documentation
- React Documentation
- Django Documentation

### Tools
- Postman/Insomnia (API testing)
- Docker (containerization)
- GitHub Actions (CI/CD)
- Sentry (error tracking)

### Learning
- FreeCodeCamp
- The Odin Project
- Full Stack Open
- AWS Training
