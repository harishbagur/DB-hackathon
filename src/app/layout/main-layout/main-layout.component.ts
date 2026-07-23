import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss'
})
export class MainLayoutComponent {
  navItems = [
    { label: 'Dashboard', icon: 'grid', route: '/dashboard' },
    { label: 'AI Assistant', icon: 'sparkles', route: '/ai-assistant' },
    { label: 'Incidents', icon: 'alert-triangle', route: '/incidents' },
    { label: 'Knowledge Base', icon: 'book-open', route: '/knowledge-base' },
    { label: 'AI Agents', icon: 'bot', route: '/ai-agents' },
    { label: 'DORA Compliance', icon: 'shield-check', route: '/dora-compliance' },
    { label: 'Reports', icon: 'bar-chart-3', route: '/reports' },
    { label: 'Escalations', icon: 'users', route: '/escalations' },
    { label: 'Settings', icon: 'settings', route: '/settings' },
  ];
}