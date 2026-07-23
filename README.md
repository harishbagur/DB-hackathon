Incidents
  GET   /api/incidents              list all incidents
  GET   /api/incidents/{id}         single incident + current state
  POST  /api/incidents/{id}/triage  trigger the full agent pipeline

Agents
  GET   /api/agents                 list all agents + live status

Chat Room
  GET   /api/incidents/{id}/room          room + all messages + members
  POST  /api/incidents/{id}/room/agents   add an agent (unix/windows)
  POST  /api/incidents/{id}/room/members  add a person from assignment group
  POST  /api/incidents/{id}/room/messages send a message
  WS    /ws/incidents/{id}                real-time events to the UI

Knowledge
  GET   /api/knowledge              list articles
  GET   /api/knowledge/search?q=    pgvector similarity search
  PATCH /api/knowledge/{id}/approve approve a draft article

Dashboard
  GET   /api/dashboard/executive    executive metrics
  GET   /api/dashboard/dora         DORA compliance scores

Escalation
  GET   /api/incidents/{id}/escalation  get escalation record
