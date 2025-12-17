import { randomUUID } from "crypto";

export interface BotSession {
  id: string;
  userId: string;
  cookies: string;
  targetId: string;
  messages: string[];
  delay: number;
  status: 'running' | 'stopped';
  messageCount: number;
  lastMessage: string;
  createdAt: Date;
  timer?: NodeJS.Timeout;
  api?: any;
}

export interface IStorage {
  createSession(session: Omit<BotSession, 'id' | 'messageCount' | 'lastMessage' | 'createdAt' | 'status'>): BotSession;
  getSession(id: string): BotSession | undefined;
  getUserSessions(userId: string): BotSession[];
  updateSession(id: string, updates: Partial<BotSession>): void;
  deleteSession(id: string): void;
  getAllSessions(): BotSession[];
}

export class MemStorage implements IStorage {
  private sessions: Map<string, BotSession>;

  constructor() {
    this.sessions = new Map();
  }

  createSession(session: Omit<BotSession, 'id' | 'messageCount' | 'lastMessage' | 'createdAt' | 'status'>): BotSession {
    const id = randomUUID();
    const newSession: BotSession = {
      ...session,
      id,
      status: 'stopped',
      messageCount: 0,
      lastMessage: '',
      createdAt: new Date(),
    };
    this.sessions.set(id, newSession);
    return newSession;
  }

  getSession(id: string): BotSession | undefined {
    return this.sessions.get(id);
  }

  getUserSessions(userId: string): BotSession[] {
    return Array.from(this.sessions.values()).filter(s => s.userId === userId);
  }

  updateSession(id: string, updates: Partial<BotSession>): void {
    const session = this.sessions.get(id);
    if (session) {
      Object.assign(session, updates);
    }
  }

  deleteSession(id: string): void {
    const session = this.sessions.get(id);
    if (session?.timer) {
      clearInterval(session.timer);
    }
    this.sessions.delete(id);
  }

  getAllSessions(): BotSession[] {
    return Array.from(this.sessions.values());
  }
}

export const storage = new MemStorage();
