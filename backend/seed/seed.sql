-- Seed file: run after alembic upgrade head
-- psql $DATABASE_URL -f seed/seed.sql

-- Users
INSERT INTO app_user (employee_id, full_name, email, department, role, location)
VALUES
  ('DB1001', 'Harish Bagur',  'harish.bagur@db.com',  'TDI',            'Vice President', 'Bangalore'),
  ('DB1002', 'John Smith',    'john.smith@db.com',    'Security',       'Engineer',       'London'),
  ('DB1003', 'Emily Brown',   'emily.brown@db.com',   'Infrastructure', 'Analyst',        'Frankfurt');

-- Incidents
INSERT INTO incident
  (incident_number, title, description, priority, status,
   affected_users, application, root_cause, created_by,
   created_at, resolved_at, platform, ci_criticality)
VALUES
  ('INC548239',
   'VPN Authentication Failure',
   'Users unable to login after security patch',
   'Critical', 'Investigating', 128, 'Global VPN', 'Authentication Service',
   1, NOW() - INTERVAL '30 minutes', NULL,
   'unix', 'tier1'),

  ('INC548240',
   'Windows Patch Failure',
   'Patch installation failed on production Windows server',
   'High', 'Resolved', 52, 'Windows Server', 'KB Package',
   2, NOW() - INTERVAL '1 day', NOW() - INTERVAL '22 hours',
   'windows', 'tier2');

-- AI Agents
INSERT INTO ai_agent (agent_name, agent_type, status, confidence_score)
VALUES
  ('Incident Lead Agent', 'Triage',          'Idle',      98),
  ('Healer Agent',        'Healing',          'Idle',      96),
  ('Listener Agent',      'Communication',    'Idle',      95),
  ('Unix Agent',          'Infrastructure',   'Idle',      92),
  ('Windows Agent',       'Infrastructure',   'Idle',      90),
  ('Knowledge Agent',     'Knowledge',        'Idle',      94);

-- Investigations
INSERT INTO ai_investigation (incident_id, agent_id, findings, recommendation, execution_time)
VALUES
  (1, 1, 'Incident pattern matched previous VPN auth failure after patch', 'Restart Authentication Service', 18),
  (1, 2, 'Found similar KB Article KB-12451', 'Refer KB-12451', 5),
  (1, 4, 'Authentication service stopped after patch rollout', 'Restart service, validate patch', 11);

-- Knowledge articles (existing approved articles)
INSERT INTO knowledge_article
  (article_number, title, category, keywords, helpful_percentage, updated_date, content, status)
VALUES
  ('KB-12451', 'VPN Authentication Failure after Patch',
   'VPN', 'VPN,Authentication,Patch',
   98, CURRENT_DATE,
   'Restart the Authentication Service after applying security patches. Validate connectivity for 10 users before full rollout.',
   'approved'),

  ('KB-32910', 'Windows Authentication Error',
   'Windows', 'Authentication,Windows,AD',
   96, CURRENT_DATE,
   'Check Active Directory replication status. Restart Netlogon service. Verify DNS resolution.',
   'approved'),

  ('KB-45781', 'Restart VPN Service',
   'Network', 'VPN,Restart,Service',
   97, CURRENT_DATE,
   'Use systemctl restart vpn-service on Unix. Verify firewall rules are intact after restart.',
   'approved');

-- DORA Compliance
INSERT INTO dora_compliance
  (operational_resilience, ict_risk, incident_management,
   business_continuity, third_party_risk, overall_score, audit_ready)
VALUES (98, 95, 96, 97, 94, 96, TRUE);

-- Escalation
INSERT INTO escalation (incident_id, assigned_team, engineer_name, reason, estimated_wait, status)
VALUES (1, 'Windows Operations', 'John Smith', 'Requires Infrastructure Approval', 5, 'Pending');

-- Executive Metrics
INSERT INTO executive_metrics
  (metric_date, automated_resolution, manual_escalation,
   avg_resolution_minutes, critical_incidents, dora_score, cyber_hygiene_score)
VALUES (CURRENT_DATE, 87, 13, 4, 5, 97, 96);

-- Playbooks (healer agent library)
INSERT INTO playbook (name, platform, trigger_keywords, action_tier, script, verify_command, description)
VALUES
  ('restart-service',
   'unix',
   'service,restart,stopped,failed,not running',
   1,
   'sudo systemctl restart {service_name}',
   'systemctl is-active {service_name}',
   'Restart a stopped or failed system service and verify it comes back up'),

  ('clear-disk-space',
   'unix',
   'disk,full,space,no space,storage,100%',
   1,
   'find /var/log -name "*.log" -mtime +7 -exec gzip {} \; && journalctl --vacuum-time=3d',
   'df -h / | awk NR==2{print $5}',
   'Compress old logs and vacuum journald to recover disk space'),

  ('flush-dns-cache',
   'windows',
   'dns,name resolution,cannot resolve,network,connectivity',
   1,
   'ipconfig /flushdns && net stop "DNS Client" && net start "DNS Client"',
   'nslookup google.com',
   'Flush DNS cache and restart DNS client service on Windows');
