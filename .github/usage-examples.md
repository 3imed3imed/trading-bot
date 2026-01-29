# Usage Examples

This document provides detailed examples of how to use the Emergent AI Builder GitHub Copilot Agent.

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Web Applications](#web-applications)
3. [API Development](#api-development)
4. [Real-Time Applications](#real-time-applications)
5. [Data Processing](#data-processing)
6. [Mobile Backends](#mobile-backends)
7. [DevOps & Infrastructure](#devops--infrastructure)

## Basic Usage

### Example 1: Simple To-Do App

**Prompt:**
```
@emergent-builder Create a simple to-do application with the following features:
- Add, edit, and delete tasks
- Mark tasks as complete
- Filter tasks by status
- Local storage persistence
```

**What You'll Get:**
- Complete React application with Vite
- Task management logic
- LocalStorage integration
- Responsive UI with CSS
- Setup and run instructions

### Example 2: Contact Form with Email

**Prompt:**
```
@emergent-builder Build a contact form that:
- Validates user input
- Sends email notifications
- Stores submissions in a database
- Returns confirmation to user
```

**What You'll Get:**
- Frontend form with validation
- Backend API with Express
- Email integration (SendGrid/Nodemailer)
- Database schema and setup
- Complete documentation

## Web Applications

### Example 3: Blog Platform

**Prompt:**
```
@emergent-builder I need a blog platform with:
- User authentication
- Create, edit, delete posts
- Markdown support
- Comments system
- Admin dashboard
- SEO optimization

Tech preference: Next.js with PostgreSQL
```

**What You'll Get:**
- Next.js app with App Router
- Authentication with NextAuth.js
- Prisma ORM setup
- Rich text editor integration
- Comment system with moderation
- Admin panel
- SEO meta tags
- Deployment guide

### Example 4: E-commerce Store

**Prompt:**
```
@emergent-builder Create an e-commerce platform with:
- Product catalog with search
- Shopping cart
- Checkout process
- Stripe payment integration
- Order management
- User profiles
- Admin inventory management
```

**What You'll Get:**
- React frontend with routing
- Node.js/Express backend
- PostgreSQL database schema
- Stripe integration
- Cart state management
- Order tracking system
- Admin dashboard
- Email notifications

### Example 5: Social Media Dashboard

**Prompt:**
```
@emergent-builder Build a social media dashboard that:
- Aggregates posts from multiple platforms
- Shows analytics and metrics
- Allows scheduling posts
- User authentication
- Real-time updates
```

**What You'll Get:**
- React dashboard with charts
- WebSocket for real-time updates
- Third-party API integrations
- Scheduling system with cron jobs
- Analytics visualization
- Authentication system

## API Development

### Example 6: REST API for Bookstore

**Prompt:**
```
@emergent-builder Create a REST API for a bookstore with:
- Books CRUD operations
- Categories and authors
- Search and filtering
- Authentication with JWT
- Rate limiting
- API documentation

Language: Python with FastAPI
```

**What You'll Get:**
- FastAPI application structure
- SQLAlchemy models
- CRUD operations
- JWT authentication
- Search endpoints
- OpenAPI documentation
- Docker setup
- Tests

### Example 7: GraphQL API

**Prompt:**
```
@emergent-builder Build a GraphQL API for a movie database with:
- Movies, actors, directors
- Relations between entities
- Queries and mutations
- Authentication
- Pagination
- Caching
```

**What You'll Get:**
- Apollo Server setup
- GraphQL schema definitions
- Resolvers
- DataLoader for batching
- Authentication middleware
- Redis caching
- Query optimization

## Real-Time Applications

### Example 8: Chat Application

**Prompt:**
```
@emergent-builder Create a real-time chat application with:
- Multiple chat rooms
- Private messaging
- User presence (online/offline)
- Message history
- File sharing
- Typing indicators
```

**What You'll Get:**
- React chat interface
- WebSocket server (Socket.io)
- User presence system
- Message persistence
- File upload handling
- Notification system
- Responsive design

### Example 9: Collaborative Whiteboard

**Prompt:**
```
@emergent-builder Build a collaborative whiteboard where:
- Multiple users can draw simultaneously
- Real-time cursor tracking
- Undo/redo functionality
- Save and share boards
- Export as image
```

**What You'll Get:**
- Canvas-based drawing interface
- WebSocket synchronization
- State management for drawing
- User cursor visualization
- History management
- Export functionality

### Example 10: Live Polling App

**Prompt:**
```
@emergent-builder Create a live polling application with:
- Create polls with multiple options
- Real-time vote counting
- Results visualization
- Anonymous or authenticated voting
- Share polls via link
```

**What You'll Get:**
- React polling interface
- Real-time vote updates
- Chart visualization
- Backend vote management
- Share functionality
- Results dashboard

## Data Processing

### Example 11: CSV Data Processor

**Prompt:**
```
@emergent-builder Build a data processing pipeline that:
- Accepts CSV file uploads
- Validates data format
- Cleans and transforms data
- Stores in PostgreSQL
- Provides data export
- Generates reports

Language: Python
```

**What You'll Get:**
- FastAPI file upload endpoint
- Pandas data processing
- Validation rules
- Database models
- Export endpoints
- Report generation
- Error handling

### Example 12: Log Analytics Tool

**Prompt:**
```
@emergent-builder Create a log analytics tool that:
- Ingests log files
- Parses different formats
- Stores in time-series database
- Provides search interface
- Shows visualizations
- Alerts on patterns
```

**What You'll Get:**
- Log ingestion service
- Parser for multiple formats
- TimescaleDB setup
- Search API
- Dashboard with charts
- Alert system
- Query optimization

## Mobile Backends

### Example 13: Mobile App Backend

**Prompt:**
```
@emergent-builder Build a backend for a fitness tracking mobile app with:
- User registration and authentication
- Activity tracking endpoints
- Achievement system
- Social features (friends, leaderboards)
- Push notifications
- Data synchronization
```

**What You'll Get:**
- REST API with Express
- JWT authentication
- Activity tracking endpoints
- Friends system
- Leaderboard logic
- Push notification setup
- Sync mechanism

### Example 14: Food Delivery API

**Prompt:**
```
@emergent-builder Create a backend for a food delivery app with:
- Restaurant management
- Menu and ordering system
- Real-time order tracking
- Payment processing
- Driver assignment
- Reviews and ratings
```

**What You'll Get:**
- Microservices architecture
- Restaurant API
- Order management system
- Real-time tracking with WebSocket
- Payment integration
- Driver matching algorithm
- Review system

## DevOps & Infrastructure

### Example 15: CI/CD Pipeline

**Prompt:**
```
@emergent-builder Set up a CI/CD pipeline with:
- Automated testing on push
- Docker image building
- Deployment to staging
- Approval for production
- Rollback capability
- Notifications

Platform: GitHub Actions
```

**What You'll Get:**
- GitHub Actions workflows
- Test automation
- Docker build steps
- Deployment scripts
- Environment management
- Notification setup
- Complete documentation

### Example 16: Monitoring Dashboard

**Prompt:**
```
@emergent-builder Create a monitoring dashboard that:
- Collects metrics from services
- Shows system health
- Visualizes performance data
- Alerts on thresholds
- Historical data analysis
```

**What You'll Get:**
- Prometheus configuration
- Grafana dashboards
- Alert rules
- Service instrumentation
- Data visualization
- Alert notifications

## Advanced Examples

### Example 17: Multi-Tenant SaaS

**Prompt:**
```
@emergent-builder Build a multi-tenant SaaS application with:
- Tenant isolation
- Subscription management
- Usage tracking and billing
- Admin portal
- API rate limiting per tenant
- Custom domains support
```

**What You'll Get:**
- Multi-tenant architecture
- Database schema with tenant isolation
- Subscription system
- Stripe billing integration
- Usage tracking
- Admin dashboard
- DNS configuration

### Example 18: AI-Powered Recommendation Engine

**Prompt:**
```
@emergent-builder Create a recommendation engine that:
- Tracks user behavior
- Analyzes preferences
- Generates personalized recommendations
- A/B testing framework
- Performance metrics
- REST API endpoints
```

**What You'll Get:**
- User behavior tracking
- Recommendation algorithm
- Machine learning integration
- A/B testing system
- Analytics dashboard
- API endpoints
- Performance optimization

## Tips for Best Results

### 1. Be Specific
❌ "Create a website"
✅ "Create a portfolio website with a homepage, project gallery, about section, and contact form"

### 2. Mention Tech Preferences
❌ "Build an API"
✅ "Build a REST API using Python FastAPI with PostgreSQL"

### 3. List Key Features
❌ "Make a blog"
✅ "Make a blog with user auth, post creation, comments, categories, and search"

### 4. Specify Integrations
❌ "Add payments"
✅ "Add Stripe payment integration with subscription support"

### 5. Include Requirements
❌ "Build it"
✅ "Build it with mobile-responsive design, SEO optimization, and Docker deployment"

## Common Follow-Up Requests

After initial generation, you can ask for:

1. **Adding Features**
   ```
   @emergent-builder Add dark mode support to the application
   ```

2. **Optimization**
   ```
   @emergent-builder Optimize the database queries for better performance
   ```

3. **Testing**
   ```
   @emergent-builder Add unit tests for the authentication system
   ```

4. **Documentation**
   ```
   @emergent-builder Generate API documentation with examples
   ```

5. **Deployment**
   ```
   @emergent-builder Create Kubernetes deployment manifests
   ```

## Getting Help

If the agent doesn't understand your request:
1. Provide more context
2. Break down into smaller tasks
3. Reference similar examples
4. Specify technologies explicitly

## Next Steps

After receiving generated code:
1. Review the code thoroughly
2. Test all functionality
3. Customize as needed
4. Deploy to your environment
5. Iterate and improve

Happy building! 🚀
