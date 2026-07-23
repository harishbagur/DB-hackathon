import { Injectable, OnDestroy } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { WsEvent } from '../models/api.models';

/**
 * WebSocket service for real-time chat room events.
 *
 * Backend events:
 *   article_list, text, system, approval_request, approval_response, member_joined
 *
 * The backend also responds to "ping" with "pong" for keep-alive.
 */
@Injectable({
  providedIn: 'root'
})
export class WebsocketService implements OnDestroy {
  private socket: WebSocket | null = null;
  private messages$ = new Subject<WsEvent>();
  private pingInterval: any;

  /**
   * Connect to the backend WebSocket for a specific incident room.
   * Closes any existing connection first.
   */
  connect(incidentId: number): void {
    this.close();

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.socket = new WebSocket(`${protocol}//${host}/ws/incidents/${incidentId}`);

    this.socket.onopen = () => {
      // Keep-alive ping every 30 seconds
      this.pingInterval = setInterval(() => {
        if (this.socket?.readyState === WebSocket.OPEN) {
          this.socket.send('ping');
        }
      }, 30_000);
    };

    this.socket.onmessage = (event) => {
      if (event.data === 'pong') return; // ignore keep-alive responses
      try {
        const parsed: WsEvent = JSON.parse(event.data);
        this.messages$.next(parsed);
      } catch {
        // Non-JSON message — emit as raw text
        this.messages$.next({ type: 'text', data: event.data });
      }
    };

    this.socket.onerror = (err) => {
      console.error('[WebsocketService] error:', err);
    };

    this.socket.onclose = () => {
      clearInterval(this.pingInterval);
    };
  }

  /**
   * Observable stream of typed WebSocket events for the connected room.
   */
  getMessages(): Observable<WsEvent> {
    return this.messages$.asObservable();
  }

  /**
   * Send a raw message over the WebSocket (e.g. for future client→server needs).
   */
  send(msg: string): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(msg);
    }
  }

  /**
   * Close the active WebSocket connection.
   */
  close(): void {
    clearInterval(this.pingInterval);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  ngOnDestroy(): void {
    this.close();
    this.messages$.complete();
  }
}
