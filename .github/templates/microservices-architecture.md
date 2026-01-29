# Microservices Architecture Guide

## Overview

A microservices architecture splits an application into small, independent services that communicate via APIs. Each service is responsible for a specific business capability.

## Project Structure

```
microservices-app/
├── services/
│   ├── api-gateway/
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── auth-service/
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── user-service/
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── product-service/
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── package.json
│   └── notification-service/
│       ├── src/
│       ├── Dockerfile
│       └── package.json
├── shared/
│   ├── types/
│   ├── utils/
│   └── middleware/
├── infrastructure/
│   ├── kubernetes/
│   ├── terraform/
│   └── docker-compose.yml
└── README.md
```

## Service Components

### 1. API Gateway

The API Gateway is the single entry point for all clients. It routes requests to appropriate microservices.

#### api-gateway/src/server.js
```javascript
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import cors from 'cors';
import rateLimit from 'express-rate-limit';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Service routes
app.use('/api/auth', createProxyMiddleware({
  target: process.env.AUTH_SERVICE_URL || 'http://auth-service:3001',
  changeOrigin: true,
  pathRewrite: { '^/api/auth': '' }
}));

app.use('/api/users', createProxyMiddleware({
  target: process.env.USER_SERVICE_URL || 'http://user-service:3002',
  changeOrigin: true,
  pathRewrite: { '^/api/users': '' }
}));

app.use('/api/products', createProxyMiddleware({
  target: process.env.PRODUCT_SERVICE_URL || 'http://product-service:3003',
  changeOrigin: true,
  pathRewrite: { '^/api/products': '' }
}));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'api-gateway' });
});

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
```

### 2. Auth Service

Handles authentication and authorization.

#### auth-service/src/server.js
```javascript
import express from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { connectDB } from './db.js';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// Register
app.post('/register', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Save user (database logic here)
    const user = await saveUser({ email, hashedPassword });
    
    res.status(201).json({ 
      message: 'User registered successfully',
      userId: user.id 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Login
app.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user (database logic here)
    const user = await findUserByEmail(email);
    
    if (!user || !await bcrypt.compare(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Generate JWT
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
    
    res.json({ token });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Verify token
app.post('/verify', (req, res) => {
  try {
    const { token } = req.body;
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    res.json({ valid: true, user: decoded });
  } catch (error) {
    res.status(401).json({ valid: false, error: 'Invalid token' });
  }
});

app.listen(PORT, () => {
  console.log(`Auth service running on port ${PORT}`);
});
```

### 3. User Service

Manages user profiles and data.

#### user-service/src/server.js
```javascript
import express from 'express';
import { verifyToken } from './middleware/auth.js';

const app = express();
const PORT = process.env.PORT || 3002;

app.use(express.json());

// Get all users
app.get('/users', verifyToken, async (req, res) => {
  try {
    // Fetch users from database
    const users = await getAllUsers();
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get user by ID
app.get('/users/:id', verifyToken, async (req, res) => {
  try {
    const user = await getUserById(req.params.id);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update user
app.put('/users/:id', verifyToken, async (req, res) => {
  try {
    const user = await updateUser(req.params.id, req.body);
    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`User service running on port ${PORT}`);
});
```

### 4. Product Service

Manages product catalog.

#### product-service/src/server.js
```javascript
import express from 'express';
import { verifyToken } from './middleware/auth.js';

const app = express();
const PORT = process.env.PORT || 3003;

app.use(express.json());

// Get all products
app.get('/products', async (req, res) => {
  try {
    const products = await getAllProducts();
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get product by ID
app.get('/products/:id', async (req, res) => {
  try {
    const product = await getProductById(req.params.id);
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.json(product);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create product (admin only)
app.post('/products', verifyToken, async (req, res) => {
  try {
    const product = await createProduct(req.body);
    res.status(201).json(product);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Product service running on port ${PORT}`);
});
```

### 5. Notification Service

Handles email, SMS, and push notifications.

#### notification-service/src/server.js
```javascript
import express from 'express';
import amqp from 'amqplib';

const app = express();
const PORT = process.env.PORT || 3004;

app.use(express.json());

// Message queue connection
let channel;

async function connectQueue() {
  const connection = await amqp.connect(process.env.RABBITMQ_URL);
  channel = await connection.createChannel();
  await channel.assertQueue('notifications');
  
  // Consume messages
  channel.consume('notifications', async (msg) => {
    const notification = JSON.parse(msg.content.toString());
    await sendNotification(notification);
    channel.ack(msg);
  });
}

connectQueue();

// Send notification endpoint
app.post('/send', async (req, res) => {
  try {
    const notification = req.body;
    
    // Add to queue
    channel.sendToQueue(
      'notifications',
      Buffer.from(JSON.stringify(notification))
    );
    
    res.json({ message: 'Notification queued' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Notification service running on port ${PORT}`);
});
```

## Shared Utilities

### shared/middleware/auth.js
```javascript
import axios from 'axios';

export async function verifyToken(req, res, next) {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    // Verify with auth service
    const response = await axios.post(
      `${process.env.AUTH_SERVICE_URL}/verify`,
      { token }
    );
    
    if (response.data.valid) {
      req.user = response.data.user;
      next();
    } else {
      res.status(401).json({ error: 'Invalid token' });
    }
  } catch (error) {
    res.status(401).json({ error: 'Authentication failed' });
  }
}
```

## Infrastructure

### docker-compose.yml
```yaml
version: '3.8'

services:
  # Databases
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"

  # Services
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "3000:3000"
    environment:
      AUTH_SERVICE_URL: http://auth-service:3001
      USER_SERVICE_URL: http://user-service:3002
      PRODUCT_SERVICE_URL: http://product-service:3003
    depends_on:
      - auth-service
      - user-service
      - product-service

  auth-service:
    build: ./services/auth-service
    ports:
      - "3001:3001"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/auth
      JWT_SECRET: your-secret-key
    depends_on:
      - postgres

  user-service:
    build: ./services/user-service
    ports:
      - "3002:3002"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/users
    depends_on:
      - postgres

  product-service:
    build: ./services/product-service
    ports:
      - "3003:3003"
    environment:
      DATABASE_URL: mongodb://mongodb:27017/products
    depends_on:
      - mongodb

  notification-service:
    build: ./services/notification-service
    ports:
      - "3004:3004"
    environment:
      RABBITMQ_URL: amqp://rabbitmq:5672
    depends_on:
      - rabbitmq

volumes:
  postgres_data:
  mongo_data:
```

## Kubernetes Deployment

### infrastructure/kubernetes/api-gateway-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: your-registry/api-gateway:latest
        ports:
        - containerPort: 3000
        env:
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:3001"
        - name: USER_SERVICE_URL
          value: "http://user-service:3002"
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: api-gateway
```

## Communication Patterns

### 1. Synchronous (HTTP/REST)
```javascript
// Service A calls Service B directly
const response = await axios.get('http://service-b/api/data');
```

### 2. Asynchronous (Message Queue)
```javascript
// Service A publishes event
channel.sendToQueue('events', Buffer.from(JSON.stringify(event)));

// Service B subscribes to events
channel.consume('events', (msg) => {
  const event = JSON.parse(msg.content.toString());
  processEvent(event);
});
```

### 3. Event-Driven
```javascript
// Publish event
await eventBus.publish('user.created', { userId: '123' });

// Subscribe to event
eventBus.on('user.created', async (data) => {
  await sendWelcomeEmail(data.userId);
});
```

## Best Practices

### 1. Service Discovery
Use service discovery tools like Consul or Kubernetes DNS

### 2. Circuit Breaker
Implement circuit breakers to handle service failures gracefully

```javascript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(asyncFunction, {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
});
```

### 3. API Versioning
Always version your APIs
```
/api/v1/users
/api/v2/users
```

### 4. Centralized Logging
Use ELK stack (Elasticsearch, Logstash, Kibana) or similar

### 5. Distributed Tracing
Implement OpenTelemetry or Jaeger for request tracing

### 6. Health Checks
Every service should have health check endpoints

### 7. Database Per Service
Each service should have its own database

## Monitoring

### Prometheus + Grafana
```javascript
import prometheus from 'prom-client';

const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status']
});

// Middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.labels(req.method, req.route?.path, res.statusCode).observe(duration);
  });
  next();
});
```

## Security

### 1. API Gateway Security
- Rate limiting
- Authentication
- Request validation
- CORS configuration

### 2. Service-to-Service Communication
- Use mutual TLS (mTLS)
- API keys or service tokens
- Network policies in Kubernetes

### 3. Data Encryption
- Encrypt data at rest
- Use TLS for data in transit

## Deployment Strategies

### Blue-Green Deployment
Deploy new version alongside old, then switch traffic

### Canary Deployment
Gradually roll out to subset of users

### Rolling Update
Update instances one by one

## Advantages

✅ Independent deployment
✅ Technology diversity
✅ Scalability
✅ Fault isolation
✅ Team autonomy

## Challenges

❌ Complexity
❌ Distributed transactions
❌ Testing difficulty
❌ Operational overhead
❌ Network latency
