# Requirements Document

## Introduction

This document specifies the requirements for transforming the psych_agent console application into a production-grade cloud-based psychiatric clinical decision support system. The system will provide a modern web interface for Subject Matter Experts (SMEs) to interact with a DSM-5-TR knowledge base through a chatbot interface, with user authentication and cost-effective cloud deployment. The architecture must support immediate deployment with continuous improvement capabilities while maintaining extensibility for future productionization.

## Glossary

- **System**: The cloud-based psychiatric clinical decision support web application
- **User**: An authenticated SME (Subject Matter Expert) with access to the application
- **Admin**: A user with privileges to manage the allow-list of authorized users
- **Chat Session**: A conversation thread between a user and the psychiatric agent
- **DSM-5-TR**: Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision
- **Vector Database**: The ChromaDB instance storing embedded DSM-5-TR content
- **Agent**: The LLM-powered psychiatric reasoning component that processes queries
- **Frontend**: The React-based user interface
- **Backend**: The Python-based API server handling business logic
- **Allow-list**: A list of email addresses or user identifiers permitted to access the system
- **Deployment Pipeline**: The automated process for deploying code changes to the cloud environment

## Requirements

### Requirement 1

**User Story:** As an SME, I want to access a modern web interface to interact with the psychiatric agent, so that I can evaluate its clinical decision support capabilities from any device with a browser.

#### Acceptance Criteria

1. WHEN a user navigates to the application URL THEN the System SHALL display a responsive web interface optimized for desktop and mobile devices
2. WHEN a user interacts with the chat interface THEN the System SHALL provide real-time feedback and maintain conversation context throughout the session
3. WHEN a user submits a query THEN the System SHALL display the agent's response with proper formatting including citations and disclaimers.
4. WHEN the user interface loads THEN the System SHALL present a clean, professional design consistent with healthcare application standards
5. WHEN a user views agent responses THEN the System SHALL clearly distinguish between reasoning steps, diagnostic criteria, and clinical disclaimers

### Requirement 2

**User Story:** As an admin, I want to control who can access the application through an allow-list, so that only authorized SMEs can use the system during the evaluation phase.

#### Acceptance Criteria

1. WHEN a user attempts to access the application THEN the System SHALL verify the user's identity against the allow-list before granting access
2. WHEN an unauthorized user attempts to access the application THEN the System SHALL deny access and display an appropriate message
3. WHEN an admin adds a user to the allow-list THEN the System SHALL immediately grant that user access to the application
4. WHEN an admin removes a user from the allow-list THEN the System SHALL revoke that user's access on their next authentication attempt
5. WHERE the allow-list is stored THEN the System SHALL persist the list in a secure, retrievable format

### Requirement 3

**User Story:** As a user, I want to authenticate securely to access the application, so that my identity is verified and my sessions are protected.

#### Acceptance Criteria

1. WHEN a user visits the application URL THEN the System SHALL present an authentication interface before allowing access to the chat functionality
2. WHEN a user provides valid credentials THEN the System SHALL create an authenticated session and redirect to the chat interface
3. WHEN a user's session expires THEN the System SHALL prompt for re-authentication without losing unsaved conversation context
4. WHEN a user logs out THEN the System SHALL terminate the session and clear sensitive data from the client
5. WHILE a user is authenticated THEN the System SHALL maintain session state across page refreshes

### Requirement 4

**User Story:** As a user, I want to have conversations with the psychiatric agent that maintain context, so that I can ask follow-up questions and refine my clinical queries.

#### Acceptance Criteria

1. WHEN a user sends a message THEN the System SHALL retrieve relevant DSM-5-TR content and generate a contextually appropriate response
2. WHEN a user sends a follow-up question THEN the System SHALL maintain the conversation history and use it to inform the response
3. WHEN the agent generates a response THEN the System SHALL include chain-of-thought reasoning, DSM-5-TR citations, and clinical disclaimers
4. WHEN the agent generates a response THEN the response SHALL include grounded citations so that the user can click on those citations to see the full context of the facts that contributed to that part of the response.
5. WHEN a user starts a new chat session THEN the System SHALL create a separate conversation thread without affecting previous sessions
6. WHEN a user views their chat history THEN the System SHALL display all messages in chronological order with clear sender identification

### Requirement 5

**User Story:** As a developer, I want the application deployed to a cost-effective cloud infrastructure with a public IP, so that SMEs can access it without requiring AWS accounts while minimizing operational costs.

#### Acceptance Criteria

1. WHEN the application is deployed THEN the System SHALL be accessible via a public IP address or domain name
2. WHEN the application is running THEN the System SHALL utilize cost-effective cloud resources that minimize monthly operational expenses
3. WHEN traffic is low THEN the System SHALL scale down resources to reduce costs without manual intervention
4. WHEN the deployment infrastructure is provisioned THEN the System SHALL use services that do not require an AWS account
5. WHEN the application is deployed THEN the System SHALL maintain persistent storage for the vector database and user data

### Requirement 6

**User Story:** As a developer, I want a smooth deployment process for code changes, so that I can iterate quickly and deploy updates without complex manual steps.

#### Acceptance Criteria

1. WHEN code changes are pushed to the repository THEN the System SHALL provide a mechanism to deploy those changes to the cloud environment
2. WHEN a deployment is initiated THEN the System SHALL complete the deployment process without requiring manual server configuration
3. WHEN a deployment fails THEN the System SHALL provide clear error messages and maintain the previous working version
4. WHEN the backend code is updated THEN the System SHALL restart the API server with the new code without data loss
5. WHEN the frontend code is updated THEN the System SHALL serve the new static assets to users on their next page load

### Requirement 7

**User Story:** As a developer, I want the codebase organized in a production-grade structure, so that the application is maintainable, extensible, and ready for future productionization.

#### Acceptance Criteria

1. WHEN the codebase is structured THEN the System SHALL separate concerns into distinct modules for frontend, backend, database, and infrastructure
2. WHEN new features are added THEN the System SHALL support extension without requiring major refactoring of existing code
3. WHEN the code is reviewed THEN the System SHALL follow Python and React best practices with clear separation of business logic, data access, and presentation layers
4. WHEN configuration is needed THEN the System SHALL use environment variables and configuration files rather than hardcoded values
5. WHEN the project structure is examined THEN the System SHALL include clear documentation for setup, development, and deployment processes

### Requirement 8

**User Story:** As a developer, I want the backend API to expose the psychiatric agent functionality through RESTful endpoints, so that the frontend can interact with the agent in a standard, scalable way.

#### Acceptance Criteria

1. WHEN the backend starts THEN the System SHALL expose API endpoints for authentication, chat operations, and health checks
2. WHEN a client sends a chat message to the API THEN the System SHALL validate the request, process it through the agent, and return a structured response
3. WHEN an API error occurs THEN the System SHALL return appropriate HTTP status codes and error messages
4. WHEN the API receives requests THEN the System SHALL validate authentication tokens and reject unauthorized requests
5. WHEN the API processes requests THEN the System SHALL handle concurrent requests without data corruption or race conditions

### Requirement 9

**User Story:** As a user, I want the application to load quickly and respond promptly, so that I can have a smooth experience without frustrating delays.

#### Acceptance Criteria

1. WHEN a user loads the application THEN the System SHALL display the initial interface within 3 seconds on a standard broadband connection
2. WHEN a user submits a query THEN the System SHALL provide immediate feedback that processing has started
3. WHEN the agent is processing a query THEN the System SHALL display a loading indicator or streaming response to maintain user engagement
4. WHEN the vector database is queried THEN the System SHALL return relevant chunks within 500 milliseconds
5. WHEN static assets are requested THEN the System SHALL serve them with appropriate caching headers to minimize load times

### Requirement 10

**User Story:** As a developer, I want the vector database and embeddings to be efficiently deployed in the cloud, so that the agent can retrieve DSM-5-TR content without requiring local file access.

#### Acceptance Criteria

1. WHEN the application is deployed THEN the System SHALL include the pre-built vector database with embedded DSM-5-TR content
2. WHEN the agent queries the vector database THEN the System SHALL retrieve results using the same embedding model used during ingestion
3. WHEN the vector database is accessed THEN the System SHALL maintain data persistence across application restarts
4. WHEN the embedding model is loaded THEN the System SHALL cache it in memory to avoid repeated loading overhead
5. WHEN the vector database is updated THEN the System SHALL support re-ingestion of documents without requiring application redeployment

### Requirement 11

**User Story:** As a developer, I want to use a cost-effective LLM solution for the psychiatric agent, so that inference costs remain minimal while maintaining clinical reasoning quality.

#### Acceptance Criteria

1. WHEN the agent generates responses THEN the System SHALL use a cost-effective LLM provider or self-hosted model
2. WHEN LLM inference is performed THEN the System SHALL optimize token usage to minimize costs per query
3. WHEN the LLM is unavailable THEN the System SHALL provide graceful error handling and retry logic
4. WHEN the LLM configuration is changed THEN the System SHALL support switching between providers without code changes
5. WHEN inference costs are evaluated THEN the System SHALL provide logging or metrics to track usage and expenses

### Requirement 12

**User Story:** As a user, I want to see my previous chat sessions, so that I can review past conversations and continue where I left off.

#### Acceptance Criteria

1. WHEN a user logs in THEN the System SHALL display a list of their previous chat sessions
2. WHEN a user selects a previous session THEN the System SHALL load and display the complete conversation history
3. WHEN a user creates a new session THEN the System SHALL add it to their session list with a timestamp and optional title
4. WHEN a user deletes a session THEN the System SHALL remove it from their history and free associated storage
5. WHEN sessions are stored THEN the System SHALL associate them with the authenticated user to prevent unauthorized access

