import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { AiAssistantComponent } from './features/ai-assistant/ai-assistant.component';

export const routes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      // Placeholder routes for navigation links
      { path: 'ai-assistant', component: AiAssistantComponent },
      { path: 'incidents', component: DashboardComponent },
      { path: 'knowledge-base', component: DashboardComponent },
      { path: 'ai-agents', component: DashboardComponent },
      { path: 'dora-compliance', component: DashboardComponent },
      { path: 'reports', component: DashboardComponent },
      { path: 'escalations', component: DashboardComponent },
      { path: 'settings', component: DashboardComponent },
    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];