swagger: '2.0'
info:
  title: AI Agent Database Query API
  description: API for querying database through AI agent
  version: 1.0.0
schemes:
  - https
produces:
  - application/json
x-google-backend:
  address: ${cloud_run_url}
  jwt_audience: ${cloud_run_url}
  protocol: h2
paths:
  /:
    get:
      summary: API root
      operationId: root
      responses:
        '200':
          description: API information
          schema:
            type: object
      x-google-backend:
        address: ${cloud_run_url}
  /health:
    get:
      summary: Health check
      operationId: healthCheck
      responses:
        '200':
          description: Service health status
          schema:
            type: object
      x-google-backend:
        address: ${cloud_run_url}
  /query:
    post:
      summary: Process AI agent query
      operationId: processQuery
      consumes:
        - application/json
      produces:
        - application/json
      parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            required:
              - query
            properties:
              query:
                type: string
                description: User query in natural language
              user_id:
                type: string
                description: Optional user identifier
              context:
                type: object
                description: Optional additional context
      responses:
        '200':
          description: Query processed successfully
          schema:
            type: object
            properties:
              response:
                type: string
              data:
                type: object
              query_id:
                type: string
              timestamp:
                type: string
        '400':
          description: Bad request
        '500':
          description: Internal server error
      x-google-backend:
        address: ${cloud_run_url}
  /queries/{query_id}:
    get:
      summary: Get query result
      operationId: getQueryResult
      parameters:
        - in: path
          name: query_id
          required: true
          type: string
          description: Query ID
      responses:
        '200':
          description: Query result
          schema:
            type: object
        '404':
          description: Query not found
        '500':
          description: Internal server error
      x-google-backend:
        address: ${cloud_run_url}
