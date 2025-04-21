"""
WebSocket connection management for the face swap benchmark.

This module provides a simple WebSocket connection manager to handle
real-time updates during benchmark runs.
"""

import logging
from typing import List, Dict, Any
from fastapi import WebSocket

# Configure logger
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    
    This class handles connecting, disconnecting, and broadcasting messages
    to all active WebSocket connections.
    """
    
    def __init__(self):
        """Initialize the connection manager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept a new WebSocket connection and add it to the active connections.
        
        Args:
            websocket: The WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"New WebSocket connection accepted. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from the active connections.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        self.active_connections.remove(websocket)
        logger.debug(f"WebSocket connection disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all active WebSocket connections.
        
        Args:
            message: The message to broadcast as a JSON-serializable dictionary
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return
            
        logger.debug(f"Broadcasting message to {len(self.active_connections)} connections")
        
        # Keep track of connections that failed to receive the message
        disconnected = []
        
        for i, connection in enumerate(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to connection {i}: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            try:
                self.active_connections.remove(conn)
                logger.info(f"Removed disconnected WebSocket connection. Remaining: {len(self.active_connections)}")
            except ValueError:
                pass  # Connection was already removed