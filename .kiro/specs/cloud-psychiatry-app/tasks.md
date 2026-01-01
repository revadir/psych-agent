# Implementation Plan

- [x] 1. Restructure project for production-grade organization
  - Create new directory structure separating frontend, backend, data, and scripts
  - Move existing agent code into backend services
  - Move ingest.py into scripts directory
  - Create configuration files for environment variables
  - Update .gitignore for new structure
  - _Requirements: 7.1, 7.3, 7.4_

- [x] 2. Set up backend FastAPI application foundation
  - Create FastAPI app with main.py entry point
  - Implement CORS middleware with configurable origins
  - Set up configuration management using Pydantic Settings
  - Create health check endpoint
  - Implement structured logging
  - _Requirements: 8.1, 7.4_

- [ ]* 2.1 Write unit tests for backend foundation
  - Test health endpoint returns correct status
  - Test CORS configuration
  - Test configuration loading from environment
  - _Requirements: 8.1_

- [x] 3. Implement database models and initialization
  - Create SQLAlchemy models for User, ChatSession, Message, and Allowlist
  - Implement database initialization script
  - Create database session management with dependency injection
  - Add database migration support with Alembic
  - _Requirements: 7.1_

- [ ]* 3.1 Write property test for data persistence
  - **Property 5: Data Persistence Across Restarts**
  - **Validates: Requirements 2.5, 5.5, 10.3**

- [ ]* 3.2 Write unit tests for database models
  - Test model creation and validation
  - Test relationships between models
  - Test database session lifecycle
  - _Requirements: 7.1_

- [x] 4. Implement authentication service and endpoints
  - Create JWT token generation and validation utilities
  - Implement authentication service with allow-list checking
  - Create auth middleware for protected routes
  - Implement POST /api/auth/login endpoint
  - Implement GET /api/auth/me endpoint
  - Implement POST /api/auth/logout endpoint
  - _Requirements: 3.1, 3.2, 3.4, 2.1_

- [ ]* 4.1 Write property test for allow-list access enforcement
  - **Property 3: Allow-list Access Enforcement**
  - **Validates: Requirements 2.1**

- [ ]* 4.2 Write property test for session authentication round-trip
  - **Property 6: Session Authentication Round-trip**
  - **Validates: Requirements 3.2, 3.5**

- [ ]* 4.3 Write property test for session cleanup on logout
  - **Property 7: Session Cleanup on Logout**
  - **Validates: Requirements 3.4**

- [ ]* 4.4 Write property test for authentication token validation
  - **Property 13: Authentication Token Validation**
  - **Validates: Requirements 8.4**

- [ ]* 4.5 Write unit tests for authentication endpoints
  - Test login with valid credentials
  - Test login with invalid credentials
  - Test token validation
  - Test logout functionality
  - _Requirements: 3.1, 3.2, 3.4_

- [x] 5. Implement admin endpoints for allow-list management
  - Create admin authorization decorator
  - Implement POST /api/admin/allowlist endpoint
  - Implement DELETE /api/admin/allowlist/{email} endpoint
  - Implement GET /api/admin/allowlist endpoint
  - Create initialization script for adding first admin
  - _Requirements: 2.3, 2.4_

- [ ]* 5.1 Write property test for allow-list state consistency
  - **Property 4: Allow-list State Consistency**
  - **Validates: Requirements 2.3, 2.4**

- [ ]* 5.2 Write unit tests for admin endpoints
  - Test adding user to allow-list
  - Test removing user from allow-list
  - Test admin authorization
  - _Requirements: 2.3, 2.4_

- [x] 6. Refactor agent service for API integration
  - Extract agent logic from agent.py into AgentService class
  - Implement vector database service wrapper
  - Add configuration for LLM provider (OpenRouter/Groq)
  - Implement response formatting with citations and disclaimers
  - Add error handling for LLM failures
  - _Requirements: 4.1, 4.3, 11.3_

- [ ]* 6.1 Write property test for agent response structure
  - **Property 1: Agent Response Structure Completeness**
  - **Validates: Requirements 1.3, 1.5, 4.3**

- [ ]* 6.2 Write property test for embedding model consistency
  - **Property 17: Embedding Model Consistency**
  - **Validates: Requirements 10.2**

- [ ]* 6.3 Write property test for embedding model caching
  - **Property 18: Embedding Model Caching**
  - **Validates: Requirements 10.4**

- [ ]* 6.4 Write property test for LLM error resilience
  - **Property 19: LLM Error Resilience**
  - **Validates: Requirements 11.3**

- [ ]* 6.5 Write unit tests for agent service
  - Test vector database query
  - Test LLM response generation
  - Test response formatting
  - Test error handling
  - _Requirements: 4.1, 4.3_

- [x] 7. Implement chat session management service
  - Create ChatService for session CRUD operations
  - Implement session creation with user association
  - Implement session retrieval with user filtering
  - Implement session deletion with cascade
  - Add message storage and retrieval
  - _Requirements: 4.4, 12.1, 12.2, 12.3, 12.4_

- [ ]* 7.1 Write property test for session isolation
  - **Property 8: Session Isolation**
  - **Validates: Requirements 4.4**

- [ ]* 7.2 Write property test for message chronological ordering
  - **Property 9: Message Chronological Ordering**
  - **Validates: Requirements 4.5**

- [ ]* 7.3 Write property test for session creation consistency
  - **Property 23: Session Creation Consistency**
  - **Validates: Requirements 12.3**

- [ ]* 7.4 Write property test for session deletion cascade
  - **Property 24: Session Deletion Cascade**
  - **Validates: Requirements 12.4**

- [ ]* 7.5 Write property test for session access control
  - **Property 25: Session Access Control**
  - **Validates: Requirements 12.5**

- [ ]* 7.6 Write unit tests for chat service
  - Test session creation
  - Test session retrieval
  - Test message storage
  - Test session deletion
  - _Requirements: 4.4, 12.1, 12.2, 12.3, 12.4_

- [x] 8. Implement chat API endpoints
  - Create POST /api/chat/sessions endpoint
  - Create GET /api/chat/sessions endpoint
  - Create GET /api/chat/sessions/{session_id} endpoint
  - Create POST /api/chat/sessions/{session_id}/messages endpoint
  - Create DELETE /api/chat/sessions/{session_id} endpoint
  - Integrate AgentService with message endpoint
  - _Requirements: 4.1, 4.2, 4.4, 4.5, 8.2_

- [ ]* 8.1 Write property test for conversation context preservation
  - **Property 2: Conversation Context Preservation**
  - **Validates: Requirements 1.2, 4.2**

- [ ]* 8.2 Write property test for API request validation
  - **Property 11: API Request Validation**
  - **Validates: Requirements 8.2**

- [ ]* 8.3 Write property test for API error response consistency
  - **Property 12: API Error Response Consistency**
  - **Validates: Requirements 8.3**

- [ ]* 8.4 Write property test for concurrent request safety
  - **Property 14: Concurrent Request Safety**
  - **Validates: Requirements 8.5**

- [ ]* 8.5 Write property test for user session retrieval
  - **Property 21: User Session Retrieval**
  - **Validates: Requirements 12.1**

- [ ]* 8.6 Write property test for session message completeness
  - **Property 22: Session Message Completeness**
  - **Validates: Requirements 12.2**

- [ ]* 8.7 Write unit tests for chat endpoints
  - Test session creation endpoint
  - Test session list endpoint
  - Test message sending endpoint
  - Test session deletion endpoint
  - _Requirements: 4.1, 4.2, 4.4, 4.5_

- [x] 9. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Initialize React frontend with Vite
  - Create React app with TypeScript using Vite
  - Set up TailwindCSS for styling
  - Configure build output for backend static serving
  - Set up React Router for navigation
  - Create basic app structure with routing
  - _Requirements: 1.1, 7.1_
