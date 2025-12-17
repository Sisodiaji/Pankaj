import type { Express, Request } from "express";
import { type Server } from "http";
import { Server as SocketIOServer } from "socket.io";
import { storage } from "./storage";
import multer from "multer";

const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 5 * 1024 * 1024 }
});

let io: SocketIOServer;

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Setup Socket.IO
  io = new SocketIOServer(httpServer, {
    cors: {
      origin: "*",
      methods: ["GET", "POST"]
    }
  });

  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);
    
    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
    });
  });

  // Get all sessions for a user
  app.get('/api/sessions', (req, res) => {
    const userId = req.headers['x-user-id'] as string || 'default-user';
    const sessions = storage.getUserSessions(userId);
    
    // Sanitize sessions to avoid circular JSON issues
    const sanitizedSessions = sessions.map(session => ({
      id: session.id,
      targetId: session.targetId,
      status: session.status,
      messageCount: session.messageCount,
      lastMessage: session.lastMessage,
      createdAt: session.createdAt,
      delay: session.delay
    }));
    
    res.json({ sessions: sanitizedSessions });
  });

  // Start a new bot session
  app.post('/api/sessions/start', upload.single('messageFile'), async (req: Request & { file?: Express.Multer.File }, res) => {
    try {
      const { cookies, targetId, delay, messages: messagesText } = req.body;
      const userId = req.headers['x-user-id'] as string || 'default-user';

      if (!cookies || !targetId || !delay) {
        return res.status(400).json({ error: 'Missing required fields' });
      }

      // Parse messages from text or file
      let messages: string[] = [];
      if (req.file) {
        const fs = await import('fs');
        const fileContent = fs.readFileSync(req.file.path, 'utf-8');
        messages = fileContent.split('\n').filter(line => line.trim());
        fs.unlinkSync(req.file.path); // cleanup
      } else if (messagesText) {
        messages = messagesText.split('\n').filter((line: string) => line.trim());
      }

      if (messages.length === 0) {
        return res.status(400).json({ error: 'No messages provided' });
      }

      // Create session
      const session = storage.createSession({
        userId,
        cookies,
        targetId,
        messages,
        delay: parseInt(delay)
      });

      // Dynamic import of ws3-fca (CommonJS module)
      const wiegine: any = await import('ws3-fca');
      const loginFn = wiegine.login || wiegine.default?.login;
      
      if (typeof loginFn !== 'function') {
        storage.deleteSession(session.id);
        return res.status(500).json({ error: 'ws3-fca login function not found' });
      }

      // Login with cookies
      loginFn(cookies, {}, (err: any, api: any) => {
        if (err) {
          console.error('Login error:', err);
          storage.deleteSession(session.id);
          return res.status(500).json({ error: 'Failed to login with cookies' });
        }

        let currentIndex = 0;
        
        // Start message sending loop
        const timer = setInterval(() => {
          const message = messages[currentIndex];
          
          api.sendMessage(message, targetId, (sendErr: any) => {
            if (sendErr) {
              console.error('Message send error:', sendErr);
              return;
            }

            const updatedSession = storage.getSession(session.id);
            if (updatedSession) {
              storage.updateSession(session.id, {
                messageCount: updatedSession.messageCount + 1,
                lastMessage: message
              });

              // Emit update via Socket.IO
              io.emit('session-update', {
                sessionId: session.id,
                messageCount: updatedSession.messageCount + 1,
                lastMessage: message,
                timestamp: new Date().toISOString()
              });
            }

            currentIndex = (currentIndex + 1) % messages.length;
          });
        }, parseInt(delay) * 1000);

        // Update session with timer and API
        storage.updateSession(session.id, {
          status: 'running',
          timer,
          api
        });

        res.json({ 
          success: true, 
          sessionId: session.id,
          message: 'Session started successfully'
        });
      });

    } catch (error: any) {
      console.error('Session start error:', error);
      res.status(500).json({ error: error.message });
    }
  });

  // Stop a session
  app.post('/api/sessions/:id/stop', (req, res) => {
    const { id } = req.params;
    const session = storage.getSession(id);

    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }

    if (session.timer) {
      clearInterval(session.timer);
    }

    if (session.api && typeof session.api.logout === 'function') {
      session.api.logout();
    }

    storage.updateSession(id, {
      status: 'stopped',
      timer: undefined,
      api: undefined
    });

    io.emit('session-update', {
      sessionId: id,
      status: 'stopped'
    });

    res.json({ success: true, message: 'Session stopped' });
  });

  // Delete a session
  app.delete('/api/sessions/:id', (req, res) => {
    const { id } = req.params;
    const session = storage.getSession(id);

    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }

    if (session.timer) {
      clearInterval(session.timer);
    }

    if (session.api && typeof session.api.logout === 'function') {
      session.api.logout();
    }

    storage.deleteSession(id);
    
    io.emit('session-deleted', { sessionId: id });

    res.json({ success: true, message: 'Session deleted' });
  });

  // Get session details
  app.get('/api/sessions/:id', (req, res) => {
    const { id } = req.params;
    const session = storage.getSession(id);

    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }

    // Don't send sensitive data
    const sanitized = {
      id: session.id,
      targetId: session.targetId,
      status: session.status,
      messageCount: session.messageCount,
      lastMessage: session.lastMessage,
      createdAt: session.createdAt,
      delay: session.delay
    };

    res.json(sanitized);
  });

  return httpServer;
}
