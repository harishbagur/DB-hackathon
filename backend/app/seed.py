"""
Seed the database with demo data.
Called automatically on startup if the database is empty.
"""
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.incident import Incident
from app.models.agent import AIAgent
from app.models.investigation import AIInvestigation
from app.models.knowledge import KnowledgeArticle
from app.models.compliance import DoraCompliance
from app.models.escalation import Escalation
from app.models.metrics import ExecutiveMetrics
from app.models.playbook import Playbook


def seed_db(db: Session) -> None:
    """Insert demo data if tables are empty."""

    # Check if already seeded
    if db.query(User).first():
        return

    now = datetime.utcnow()

    # ── Users ──────────────────────────────────────────────
    users = [
        User(employee_id="DB1001", full_name="Harish Bagur", email="harish.bagur@db.com",
             department="TDI", role="Vice President", location="Bangalore"),
        User(employee_id="DB1002", full_name="John Smith", email="john.smith@db.com",
             department="Security", role="Engineer", location="London"),
        User(employee_id="DB1003", full_name="Emily Brown", email="emily.brown@db.com",
             department="Infrastructure", role="Analyst", location="Frankfurt"),
    ]
    db.add_all(users)
    db.flush()

    # ── Incidents ──────────────────────────────────────────
    incidents = [
        Incident(
            incident_number="INC548239",
            title="VPN Authentication Failure",
            description="Users unable to login after security patch",
            priority="Critical", status="Investigating",
            affected_users=128, application="Global VPN",
            root_cause="Authentication Service", created_by=1,
            created_at=now - timedelta(minutes=30), resolved_at=None,
            platform="unix", ci_criticality="tier1",
        ),
        Incident(
            incident_number="INC548240",
            title="Windows Patch Failure",
            description="Patch installation failed on production Windows server",
            priority="High", status="Resolved",
            affected_users=52, application="Windows Server",
            root_cause="KB Package", created_by=2,
            created_at=now - timedelta(days=1), resolved_at=now - timedelta(hours=22),
            platform="windows", ci_criticality="tier2",
        ),
    ]
    db.add_all(incidents)
    db.flush()

    # ── AI Agents ──────────────────────────────────────────
    agents = [
        AIAgent(agent_name="Incident Lead Agent", agent_type="Triage", status="Idle", confidence_score=98),
        AIAgent(agent_name="Healer Agent", agent_type="Healing", status="Idle", confidence_score=96),
        AIAgent(agent_name="Listener Agent", agent_type="Communication", status="Idle", confidence_score=95),
        AIAgent(agent_name="Unix Agent", agent_type="Infrastructure", status="Idle", confidence_score=92),
        AIAgent(agent_name="Windows Agent", agent_type="Infrastructure", status="Idle", confidence_score=90),
        AIAgent(agent_name="Knowledge Agent", agent_type="Knowledge", status="Idle", confidence_score=94),
    ]
    db.add_all(agents)
    db.flush()

    # ── Investigations ─────────────────────────────────────
    investigations = [
        AIInvestigation(incident_id=1, agent_id=1,
                        findings="Incident pattern matched previous VPN auth failure after patch",
                        recommendation="Restart Authentication Service", execution_time=18),
        AIInvestigation(incident_id=1, agent_id=2,
                        findings="Found similar KB Article KB-12451",
                        recommendation="Refer KB-12451", execution_time=5),
        AIInvestigation(incident_id=1, agent_id=4,
                        findings="Authentication service stopped after patch rollout",
                        recommendation="Restart service, validate patch", execution_time=11),
    ]
    db.add_all(investigations)

    # ── Knowledge Articles ─────────────────────────────────
    articles = [
        KnowledgeArticle(
            article_number="KB-12451",
            title="VPN Authentication Failure after Patch",
            category="VPN", keywords="VPN,Authentication,Patch",
            helpful_percentage=98, updated_date=date.today(),
            content="Restart the Authentication Service after applying security patches. Validate connectivity for 10 users before full rollout.",
            status="approved",
        ),
        KnowledgeArticle(
            article_number="KB-32910",
            title="Windows Authentication Error",
            category="Windows", keywords="Authentication,Windows,AD",
            helpful_percentage=96, updated_date=date.today(),
            content="Check Active Directory replication status. Restart Netlogon service. Verify DNS resolution.",
            status="approved",
        ),
        KnowledgeArticle(
            article_number="KB-45781",
            title="Restart VPN Service",
            category="Network", keywords="VPN,Restart,Service",
            helpful_percentage=97, updated_date=date.today(),
            content="Use systemctl restart vpn-service on Unix. Verify firewall rules are intact after restart.",
            status="approved",
        ),
    ]
    db.add_all(articles)

    # ── DORA Compliance ────────────────────────────────────
    db.add(DoraCompliance(
        operational_resilience=98, ict_risk=95, incident_management=96,
        business_continuity=97, third_party_risk=94, overall_score=96,
        audit_ready=True,
    ))

    # ── Escalation ─────────────────────────────────────────
    db.add(Escalation(
        incident_id=1, assigned_team="Windows Operations",
        engineer_name="John Smith",
        reason="Requires Infrastructure Approval",
        estimated_wait=5, status="Pending",
    ))

    # ── Executive Metrics ──────────────────────────────────
    db.add(ExecutiveMetrics(
        metric_date=date.today(),
        automated_resolution=87, manual_escalation=13,
        avg_resolution_minutes=4, critical_incidents=5,
        dora_score=97, cyber_hygiene_score=96,
    ))

    # ── Playbooks ──────────────────────────────────────────
    playbooks = [
        Playbook(
            name="restart-service", platform="unix",
            trigger_keywords="service,restart,stopped,failed,not running",
            action_tier=1,
            script="sudo systemctl restart {service_name}",
            verify_command="systemctl is-active {service_name}",
            description="Restart a stopped or failed system service and verify it comes back up",
        ),
        Playbook(
            name="clear-disk-space", platform="unix",
            trigger_keywords="disk,full,space,no space,storage,100%",
            action_tier=1,
            script='find /var/log -name "*.log" -mtime +7 -exec gzip {} \\; && journalctl --vacuum-time=3d',
            verify_command="df -h / | awk NR==2{print $5}",
            description="Compress old logs and vacuum journald to recover disk space",
        ),
        Playbook(
            name="flush-dns-cache", platform="windows",
            trigger_keywords="dns,name resolution,cannot resolve,network,connectivity",
            action_tier=1,
            script='ipconfig /flushdns && net stop "DNS Client" && net start "DNS Client"',
            verify_command="nslookup google.com",
            description="Flush DNS cache and restart DNS client service on Windows",
        ),
    ]
    db.add_all(playbooks)

    db.commit()
    print("[seed] Demo data inserted successfully.")
