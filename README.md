# 🎫 Ticketing System API - Complete Documentation

## 📑 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Authentication & Authorization](#authentication--authorization)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [Data Models & Relationships](#data-models--relationships)
7. [Permission System](#permission-system)
8. [Complete Usage Examples](#complete-usage-examples)
9. [Error Handling & Validation](#error-handling--validation)
10. [Business Logic & Rules](#business-logic--rules)
11. [Best Practices](#best-practices)
12. [Deployment Guide](#deployment-guide)

---

## 🎯 Overview

This is a **multi-tenant ticketing and support management system** built with Django REST Framework. The system enables organizations to manage customer support tickets with role-based access control, agent assignment, and ticket resolution tracking.

### 🌟 Key Features

- **Multi-Company Architecture**: Support multiple companies with data isolation
- **Role-Based Access Control (RBAC)**: Owner, Admin, Agent, and User roles
- **JWT Authentication**: Secure token-based authentication with refresh capabilities
- **Ticket Management**: Create, assign, track, and resolve support tickets
- **Anonymous Ticket Access**: Allow ticket viewing via public ID without authentication
- **Agent Assignment**: Intelligent agent assignment with company validation
- **Ticket Resolution Tracking**: Complete audit trail of ticket resolutions
- **Profile Management**: Comprehensive user profile and role management

### 🎭 User Roles

| Role | Permissions | Description |
|------|------------|-------------|
| **Superuser** | Full system access | Django superuser with unrestricted access |
| **Owner** | Company management, all tickets, assign admins | Company owner, one per company |
| **Admin** | Manage tickets, assign agents | Administrative access within company |
| **Agent** | Handle assigned tickets | Support agent handling tickets |
| **User** | Create and view own tickets | Regular user/customer |

---

## 🏗️ System Architecture

### Module Overview

```
├── Authentication Module (JWT)
│   ├── Token Creation (Login)
│   └── Token Refresh
│
├── Company Module
│   ├── Company CRUD
│   ├── Company Tickets
│   └── Ownership Management
│
├── Ticket Module
│   ├── Ticket CRUD
│   ├── Agent Assignment
│   ├── Status Management
│   └── Anonymous Access
│
├── Profile Module
│   ├── User Profiles
│   ├── Role Assignment
│   └── Company Association
│
├── Registration Module
│   └── User Registration
│
└── Ticket Resolution Module
    ├── Resolution Tracking
    └── Closed Ticket Access
```

### Technology Stack

- **Framework**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL/MySQL (recommended)
- **Python**: 3.8+
- **Key Libraries**:
  - `djangorestframework`
  - `djangorestframework-simplejwt`
  - `django-cors-headers`

---

## 🔐 Authentication & Authorization

### JWT Token Authentication

The API uses JWT tokens with access and refresh token pairs for secure authentication.

#### Token Endpoints

##### 1. Login (Create Token)
```http
POST /token/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Token Lifespan:**
- Access Token: 15 minutes (configurable)
- Refresh Token: 7 days (configurable)

##### 2. Refresh Token
```http
POST /token/refresh/
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Authentication Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📚 API Endpoints Reference

### 🏢 Company Management

#### List Companies
```http
GET /companies/
Authorization: Bearer <token>
Permission: IsAuthenticated
```

**Access Rules:**
- Superusers: See all companies
- Owners: See only their own company
- Others: No access

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Business Street",
    "description": "Leading tech company",
    "created_at": "2026-01-01T10:00:00Z",
    "updated_at": "2026-01-01T10:00:00Z"
  }
]
```

#### Create Company
```http
POST /companies/
Authorization: Bearer <token>
Content-Type: application/json
Permission: IsAuthenticated
```

**Business Rules:**
- User must not already own a company
- Creating user automatically becomes the owner
- User's role is set to "owner"
- User's company is linked automatically

**Request Body:**
```json
{
  "name": "Tech Solutions Inc",
  "slug": "tech-solutions",
  "email": "contact@techsolutions.com",
  "phone": "+1987654321",
  "address": "456 Tech Avenue",
  "description": "Innovative technology solutions"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "Tech Solutions Inc",
  "slug": "tech-solutions",
  "email": "contact@techsolutions.com",
  "phone": "+1987654321",
  "address": "456 Tech Avenue",
  "description": "Innovative technology solutions",
  "created_at": "2026-01-02T14:30:00Z",
  "updated_at": "2026-01-02T14:30:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "You already own a company. Each user can only own one company."
}
```

#### Get Company Details
```http
GET /companies/{slug}/
Authorization: Bearer <token>
Permission: IsAuthenticated
```

**URL Parameters:**
- `slug`: Company slug (e.g., "acme-corp")

#### Update Company
```http
PUT /companies/{slug}/
Authorization: Bearer <token>
Content-Type: application/json
Permission: IsAuthenticated, Owner
```

#### Partial Update Company
```http
PATCH /companies/{slug}/
Authorization: Bearer <token>
Content-Type: application/json
Permission: IsAuthenticated, Owner
```

#### Delete Company
```http
DELETE /companies/{slug}/
Authorization: Bearer <token>
Permission: IsAuthenticated, Owner
```

---

### 🎫 Ticket Management

#### List Company Tickets
```http
GET /companies/{slug}/tickets/
Authorization: Bearer <token> (optional for anonymous with public_id)
```

**Access Rules:**
1. **Authenticated Users:**
   - Superusers/Owners/Admins: See all company tickets
   - Regular users: See only their own tickets

2. **Anonymous Users:**
   - Must provide `public_id` query parameter
   - Can only access tickets with matching UUID

**Query Parameters:**
- `public_id` (optional): UUID for anonymous access

**Example Requests:**
```http
# Authenticated - All tickets
GET /companies/acme-corp/tickets/
Authorization: Bearer <token>

# Anonymous - Specific ticket
GET /companies/acme-corp/tickets/?public_id=550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "public_id": "550e8400-e29b-41d4-a716-446655440000",
    "company": 1,
    "user": 5,
    "assigned_to": 3,
    "title": "Database Connection Error",
    "description": "Unable to connect to production database",
    "status": "in_progress",
    "priority": "high",
    "category": "technical",
    "created_at": "2026-01-02T10:00:00Z",
    "updated_at": "2026-01-02T15:30:00Z"
  }
]
```

#### Create Ticket
```http
POST /companies/{slug}/tickets/
Content-Type: application/json
Authorization: Bearer <token> (optional)
```

**Business Rules:**
- Authenticated users: Ticket linked to user account
- Anonymous users: Ticket created without user association
- Automatically linked to company via slug

**Request Body:**
```json
{
  "title": "Login Issue",
  "description": "Cannot log into the customer portal",
  "priority": "medium",
  "category": "account"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "public_id": "660e9500-f39c-51e5-b827-557766551111",
  "company": 1,
  "user": null,
  "assigned_to": null,
  "title": "Login Issue",
  "description": "Cannot log into the customer portal",
  "status": "open",
  "priority": "medium",
  "category": "account",
  "created_at": "2026-01-02T16:00:00Z",
  "updated_at": "2026-01-02T16:00:00Z"
}
```

#### Get Ticket Details
```http
GET /companies/{slug}/tickets/{id}/
Authorization: Bearer <token> or ?public_id=<uuid>
```

#### Update Ticket
```http
PUT /companies/{slug}/tickets/{id}/
Authorization: Bearer <token>
Content-Type: application/json
Permission: CanAccessTicket
```

#### Partial Update Ticket
```http
PATCH /companies/{slug}/tickets/{id}/
Authorization: Bearer <token>
Content-Type: application/json
Permission: CanAccessTicket
```

**Request Body Example:**
```json
{
  "status": "resolved",
  "priority": "low"
}
```

#### Delete Ticket
```http
DELETE /companies/{slug}/tickets/{id}/
Authorization: Bearer <token>
Permission: IsAuthenticated, OwnerOrAdmin
```

#### Assign Agent to Ticket
```http
POST /companies/{slug}/tickets/{id}/assign_agent/
Authorization: Bearer <token>
Content-Type: application/json
Permission: CanAssignAgent (Owner or Admin)
```

**Business Rules:**
1. Agent must belong to the same company as the ticket
2. Cannot reassign if agent is already assigned
3. Cannot assign agent to closed tickets
4. Only owners and admins can assign agents

**Request Body:**
```json
{
  "assigned_to": 3
}
```

**Response (200 OK):**
```json
{
  "detail": "john.agent has been assigned to the ticket"
}
```

**Error Responses:**

**400 Bad Request - Wrong Company:**
```json
{
  "detail": "The agent does not belong to the same company as the ticket."
}
```

**400 Bad Request - Already Assigned:**
```json
{
  "detail": "This agent is already assigned to this ticket."
}
```

**400 Bad Request - Closed Ticket:**
```json
{
  "detail": "Cannot assign agent to a closed ticket."
}
```

---

### 👤 Profile Management

#### List Profiles
```http
GET /profiles/
Authorization: Bearer <token>
Permission: IsAuthenticated
```

**Access Rules:**
- Superusers: See all profiles
- Owners/Admins: See profiles in their company
- Regular users: See only their own profile

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "john@acme.com",
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "role": "agent",
    "company": 1,
    "phone": "+1234567890",
    "is_active": true,
    "date_joined": "2026-01-01T10:00:00Z"
  }
]
```

#### Create Profile
```http
POST /profiles/
Authorization: Bearer <token>
Content-Type: application/json
Permission: IsAuthenticated, OwnerOrAdmin
```

#### Get Profile Details
```http
GET /profiles/{id}/
Authorization: Bearer <token>
Permission: IsAuthenticated
```

#### Update Profile
```http
PUT /profiles/{id}/
Authorization: Bearer <token>
Content-Type: application/json
Permission: IsAuthenticated, SelfOrAdmin
```

#### Partial Update Profile
```http
PATCH /profiles/{id}/
Authorization: Bearer <token>
Content-Type: application/json
Permission: IsAuthenticated, SelfOrAdmin
```

#### Delete Profile
```http
DELETE /profiles/{id}/
Authorization: Bearer <token>
Permission: IsAuthenticated, OwnerOrAdmin
```

#### Assign Role to User
```http
POST /profiles/{id}/assign_role/
Authorization: Bearer <token>
Content-Type: application/json
Permission: CanAssignAgent (Owner or Admin)
```

**Business Rules:**
1. Users cannot change their own role
2. Only owners can assign "admin" role
3. User must be in the same company
4. User is automatically linked to the company

**Request Body:**
```json
{
  "role": "agent"
}
```

**Response (200 OK):**
```json
{
  "detail": "User role changed to agent.",
  "user": {
    "id": 5,
    "email": "newagent@acme.com",
    "username": "new.agent",
    "first_name": "New",
    "last_name": "Agent",
    "role": "agent",
    "company": 1
  }
}
```

**Error Responses:**

**403 Forbidden - Self Assignment:**
```json
{
  "detail": "You cannot change your own role."
}
```

**403 Forbidden - Insufficient Permissions:**
```json
{
  "detail": "Only owners can assign admin role."
}
```

---

### 📝 Registration

#### Register New User
```http
POST /register/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "first_name": "New",
  "last_name": "User",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "id": 10,
  "email": "newuser@example.com",
  "username": "newuser",
  "first_name": "New",
  "last_name": "User",
  "role": "user",
  "company": null,
  "date_joined": "2026-01-02T16:45:00Z"
}
```

---

### 🔍 Ticket Resolution

#### List Ticket Resolutions
```http
GET /tickets-resolution/
Authorization: Bearer <token>
Permission: CanAccessTicketResolution
```

**Note**: Only returns tickets with status "closed" that have resolutions

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "public_id": "550e8400-e29b-41d4-a716-446655440000",
    "company": 1,
    "title": "Database Connection Error",
    "status": "closed",
    "resolution": {
      "id": 1,
      "resolution_text": "Restarted database service and cleared connection pool",
      "resolved_by": 3,
      "resolved_at": "2026-01-02T17:00:00Z"
    },
    "created_at": "2026-01-02T10:00:00Z",
    "closed_at": "2026-01-02T17:00:00Z"
  }
]
```

#### Get Resolution Details
```http
GET /tickets-resolution/{public_id}/
Authorization: Bearer <token>
Permission: CanAccessTicketResolution
```

**URL Parameters:**
- `public_id`: Ticket's public UUID

---

## 🗃️ Data Models & Relationships

### Company Model
```python
{
  "id": Integer (Primary Key),
  "name": String (max_length=255, required),
  "slug": String (max_length=255, unique, required),
  "email": Email (required),
  "phone": String (max_length=20),
  "address": Text,
  "description": Text,
  "created_at": DateTime (auto),
  "updated_at": DateTime (auto)
}
```

**Relationships:**
- `tickets`: One-to-Many with Ticket
- `users`: One-to-Many with User

### User/Profile Model
```python
{
  "id": Integer (Primary Key),
  "email": Email (unique, required),
  "username": String (unique, required),
  "first_name": String (max_length=150),
  "last_name": String (max_length=150),
  "password": String (hashed),
  "role": String (choices: ['user', 'agent', 'admin', 'owner']),
  "company": ForeignKey (Company, nullable),
  "phone": String (max_length=20),
  "is_active": Boolean (default=True),
  "is_staff": Boolean (default=False),
  "is_superuser": Boolean (default=False),
  "date_joined": DateTime (auto),
  "last_login": DateTime
}
```

**Relationships:**
- `company`: Many-to-One with Company
- `created_tickets`: One-to-Many with Ticket (as user)
- `assigned_tickets`: One-to-Many with Ticket (as agent)

### Ticket Model
```python
{
  "id": Integer (Primary Key),
  "public_id": UUID (unique, auto-generated),
  "company": ForeignKey (Company, required),
  "user": ForeignKey (User, nullable),
  "assigned_to": ForeignKey (User, nullable, related_name='assigned_tickets'),
  "title": String (max_length=255, required),
  "description": Text (required),
  "status": String (choices: ['open', 'in_progress', 'resolved', 'closed']),
  "priority": String (choices: ['low', 'medium', 'high', 'urgent']),
  "category": String (max_length=100),
  "created_at": DateTime (auto),
  "updated_at": DateTime (auto)
}
```

**Relationships:**
- `company`: Many-to-One with Company
- `user`: Many-to-One with User (creator)
- `assigned_to`: Many-to-One with User (agent)
- `resolution`: One-to-One with TicketResolution

### TicketResolution Model
```python
{
  "id": Integer (Primary Key),
  "ticket": OneToOneField (Ticket, required),
  "resolution_text": Text (required),
  "resolved_by": ForeignKey (User, required),
  "resolved_at": DateTime (auto),
  "created_at": DateTime (auto),
  "updated_at": DateTime (auto)
}
```

**Relationships:**
- `ticket`: One-to-One with Ticket
- `resolved_by`: Many-to-One with User

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Company   │◄───────┤     User     ├────────►│   Ticket    │
│             │ 1     * │              │ 1     * │             │
│ - name      │         │ - email      │         │ - title     │
│ - slug      │         │ - role       │         │ - status    │
│ - email     │         │ - company_id │         │ - priority  │
└─────────────┘         └──────────────┘         └──────┬──────┘
                               │                        │ 1
                               │ *                      │
                               │                        │ 1
                        ┌──────▼──────┐         ┌──────▼──────────┐
                        │   Ticket    │         │ TicketResolution│
                        │ (assigned)  │         │                 │
                        └─────────────┘         │ - resolution    │
                                                │ - resolved_by   │
                                                └─────────────────┘
```

---

## 🔒 Permission System

### Custom Permission Classes

#### CanAssignAgent
**Purpose**: Control who can assign agents to tickets

**Allowed Roles:**
- Superuser
- Owner (of the company)
- Admin (of the company)

**Usage:**
```python
@action(detail=True, methods=['post'], permission_classes=[CanAssignAgent])
def assign_agent(self, request):
    # Agent assignment logic
```

#### CanAccessTicketResolution
**Purpose**: Control access to ticket resolutions

**Allowed:**
- Users who can view the associated ticket
- Company owners/admins
- Superusers

**Usage:**
```python
class TicketResolutionViewset(viewsets.ModelViewSet):
    permission_classes = [CanAccessTicketResolution]
```

### Permission Logic Flow

```
Request → Authentication Check → Role Check → Company Check → Action
   │              │                   │             │           │
   │              ├─ JWT Valid?       │             │           │
   │              │                   │             │           │
   │              ▼                   ▼             ▼           ▼
   │         Authenticated?    User Role?   Same Company?   Allowed?
   │              │                   │             │           │
   └──────────────┴───────────────────┴─────────────┴───────────┘
```

---

## 💡 Complete Usage Examples

### Example 1: Complete User Onboarding Flow

```bash
# Step 1: Register new user
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'

# Step 2: Login
curl -X POST http://localhost:8000/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
  }'

# Response: Save these tokens
# {
#   "access": "eyJ0eXAiOiJKV1Qi...",
#   "refresh": "eyJ0eXAiOiJKV1Qi..."
# }

# Step 3: Create a company (user becomes owner)
curl -X POST http://localhost:8000/companies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -d '{
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Business Street",
    "description": "Leading tech solutions provider"
  }'
```

### Example 2: Support Ticket Lifecycle

```bash
# Step 1: Customer creates a ticket (anonymous)
curl -X POST http://localhost:8000/companies/acme-corp/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cannot access dashboard",
    "description": "Getting 404 error when trying to access the dashboard",
    "priority": "high",
    "category": "technical"
  }'

# Response: Save the public_id for tracking
# {
#   "id": 15,
#   "public_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "open",
#   ...
# }

# Step 2: Customer checks ticket status (anonymous)
curl -X GET "http://localhost:8000/companies/acme-corp/tickets/?public_id=550e8400-e29b-41d4-a716-446655440000"

# Step 3: Owner assigns agent to ticket
curl -X POST http://localhost:8000/companies/acme-corp/tickets/15/assign_agent/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -d '{
    "assigned_to": 8
  }'

# Step 4: Agent updates ticket status
curl -X PATCH http://localhost:8000/companies/acme-corp/tickets/15/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <agent_token>" \
  -d '{
    "status": "in_progress"
  }'

# Step 5: Agent resolves ticket
curl -X PATCH http://localhost:8000/companies/acme-corp/tickets/15/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <agent_token>" \
  -d '{
    "status": "resolved"
  }'
```

### Example 3: Team Management

```bash
# Step 1: Owner adds new team member
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "agent@acme.com",
    "username": "support.agent",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Support",
    "last_name": "Agent"
  }'

# Step 2: Owner assigns agent role
curl -X POST http://localhost:8000/profiles/20/assign_role/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <owner_token>" \
  -d '{
    "role": "agent"
  }'

# Response:
# {
#   "detail": "User role changed to agent.",
#   "user": {
#     "id": 20,
#     "email": "agent@acme.com",
#     "role": "agent",
#     "company": 1
#   }
# }

# Step 3: List all team members
curl -X GET http://localhost:8000/profiles/ \
  -H "Authorization: Bearer <owner_token>"
```

### Example 4: Token Refresh Flow

```bash
# Step 1: Access token expires, use refresh token
curl -X POST http://localhost:8000/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1Qi..."
  }'

# Response: New access token
# {
#   "access": "eyJ0eXAiOiJKV1Qi..."
# }

# Step 2: Use new access token for requests
curl -X GET http://localhost:8000/profiles/ \
  -H "Authorization: Bearer <new_access_token>"
```

### Example 5: Viewing Ticket Resolutions

```bash
# Step 1: Get all resolved tickets
curl -X GET http://localhost:8000/tickets-resolution/ \
  -H "Authorization: Bearer <token>"

# Step 2: Get specific resolution details
curl -X GET http://localhost:8000/tickets-resolution/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer <token>"
```

---

## ⚠️ Error Handling & Validation

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Invalid request data or business rule violation |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Common Error Responses

#### Authentication Errors

**Missing Token:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Invalid Token:**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

**Expired Token:**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

#### Permission Errors

**Insufficient Permissions:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Cannot Change Own Role:**
```json
{
  "detail": "You cannot change your own role."
}
```

**Only Owners Can Assign Admin:**
```json
{
  "detail": "Only owners can assign admin role."
}
```

#### Validation Errors

**Field Validation:**
```json
{
  "email": ["Enter a valid email address."],
  "password": ["This field is required."],
  "slug": ["This field must be unique."]
}
```

**Business Rule Violations:**
```json
{
  "error": "You already own a company. Each user can only own one company."
}
```

**Agent Assignment Errors:**
```json
{
  "detail": "The agent does not belong to the same company as the ticket."
}
```

```json
{
  "detail": "Cannot assign agent to a closed ticket."
}
```

#### Resource Not Found

```json
{
  "detail": "Not found."
}
```

---

## 📋 Business Logic & Rules

### Company Management Rules

1. **One Company Per User (as Owner)**
   - Each user can own only one company
   - Enforced at company creation
   - User automatically becomes "owner" role

2. **Company Ownership**
   - Creating user automatically linked as owner
   - User's role changed to "owner"
   - Owner has full company access

### Ticket Management Rules

1. **Ticket Creation**
   - Anonymous users can create tickets
   - Authenticated users have tickets linked to their account
   - All tickets require valid company slug

2. **Ticket Access**
   - **Authenticated Access:**
     - Superusers: All tickets
     - Owners/Admins: All company tickets
     - Regular users: Only their own tickets
   
   - **Anonymous Access:**
     - Must provide valid UUID via `public_id` parameter
     - Can only view that specific ticket

3. **Agent Assignment**
   - Only owners and admins can assign agents
   - Agent must belong to the same company
   - Cannot reassign same agent
   - Cannot assign to closed tickets

4. **Ticket Status Flow**
   ```
   open → in_progress → resolved → closed
   ```

### Profile & Role Management Rules

1. **Role Hierarchy**
   ```
   superuser > owner > admin > agent > user
   ```

2. **Role Assignment**
   - Users cannot change their own role
   - Only owners can assign "admin" role
   - Admins can assign "agent" and "user" roles
   - Role assignment requires CanAssignAgent permission

3. **Profile Access**
   - Users can view their own profile
   - Owners/admins can view company profiles
   - Superusers can view all profiles

### Resolution Tracking Rules

1. **Resolution Access**
   - Only closed tickets have resolutions
   - Read-only access (HTTP GET only)
   - Requires CanAccessTicketResolution permission

---

---


### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up HTTPS/SSL
- [ ] Configure allowed hosts
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure email backend
- [ ] Set up static/media file serving
- [ ] Enable database backups
- [ ] Set up CI/CD pipeline

---

## 📊 API Response Examples

### Successful Responses

#### Company Created
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "address": "123 Business Street",
  "description": "Leading tech solutions",
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": "2026-01-02T10:00:00Z"
}
```

#### Ticket Created
```json
{
  "id": 15,
  "public_id": "550e8400-e29b-41d4-a716-446655440000",
  "company": 1,
  "user": 5,
  "assigned_to": null,
  "title": "Login Issue",
  "description": "Cannot access dashboard",
  "status": "open",
  "priority": "high",
  "category": "technical",
  "created_at": "2026-01-02T14:30:00Z",
  "updated_at": "2026-01-02T14:30:00Z"
}
```

#### Agent Assigned
```json
{
  "detail": "john.agent has been assigned to the ticket"
}
```

#### Role Changed
```json
{
  "detail": "User role changed to agent.",
  "user": {
    "id": 10,
    "email": "agent@acme.com",
    "username": "support.agent",
    "first_name": "Support",
    "last_name": "Agent",
    "role": "agent",
    "company": 1
  }
}
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue 1: Token Not Working
**Symptoms:** 401 Unauthorized errors
**Solutions:**
- Check if token is expired
- Verify token is in correct format: `Bearer <token>`
- Ensure token is included in Authorization header
- Try refreshing the token

#### Issue 2: Cannot Assign Agent
**Symptoms:** 400 Bad Request when assigning agent
**Solutions:**
- Verify agent belongs to same company
- Check if ticket is not closed
- Ensure you have owner/admin permissions
- Confirm agent_id is correct

#### Issue 3: Cannot Create Company
**Symptoms:** "You already own a company" error
**Solutions:**
- Each user can own only one company
- Use different user account
- Or transfer ownership of existing company

#### Issue 4: Anonymous Ticket Access Not Working
**Symptoms:** Empty results or 404
**Solutions:**
- Ensure `public_id` is valid UUID format
- Check company slug is correct
- Verify ticket exists in that company

---

## 📞 Support & Resources

### API Documentation
- Swagger/OpenAPI: `/api/docs/ or http://localhost:8000/swagger/`
- ReDoc: `/api/redoc/ or http://localhost:8000/swagger/redoc`

### Development Tools
- Postman Collection: Available on request

---

## 📝 Changelog

### Version 1.0.0 (January 2026)
- Initial release
- Multi-company support
- JWT authentication
- Ticket management system
- Agent assignment functionality
- Role-based access control
- Ticket resolution tracking
- Anonymous ticket access


---

## 🙏 Acknowledgments

Built with:
- Django REST Framework
- Simple JWT
- PostgreSQL
- Python 3.8+

---

**Last Updated:** January 2, 2026  
**Version:** 1.0.0  
**Maintained by:** Brian Ojung'a
