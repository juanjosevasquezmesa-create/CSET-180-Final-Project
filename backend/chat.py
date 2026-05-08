from flask import Blueprint, session, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from .models import Complaint, Message, Conversation, ChatParticipant, User, engine

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.route("/messages/<int:complaint_id>", methods=["GET"])
def get_messages(complaint_id):
    """Fetch all messages and complaint details for a specific complaint"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    
    with Session(engine) as session_db:
        complaint = session_db.get(Complaint, complaint_id)
        
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
        
        # Check authorization - user must be either the customer or the handler
        is_customer = complaint.customer_id == user_id
        is_handler = complaint.handled_by == user_id
        is_admin = session.get("role") == "admin"
        
        if not (is_customer or is_handler or is_admin):
            return jsonify({"error": "Unauthorized"}), 403
        
        # Fetch messages related to this complaint
        messages = session_db.scalars(
            select(Message).where(Message.related_complaint_id == complaint_id)
        ).all()
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                "message_id": msg.message_id,
                "sender_name": msg.sender.name,
                "sender_id": msg.sender_id,
                "message_text": msg.message_text,
                "sent_at": msg.sent_at.isoformat() if msg.sent_at else "N/A",
                "is_current_user": msg.sender_id == user_id,
            })
        
        return jsonify({
            "complaint": {
                "complaint_id": complaint.complaint_id,
                "title": complaint.title,
                "status": complaint.status,
            },
            "messages": messages_data
        })


@chat_bp.route("/send-message/<int:complaint_id>", methods=["POST"])
def send_message(complaint_id):
    """Send a message to a complaint ticket"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    data = request.get_json()
    message_text = data.get("message", "").strip()
    
    if not message_text:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    with Session(engine) as session_db:
        complaint = session_db.get(Complaint, complaint_id)
        
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
        
        # Check authorization
        is_customer = complaint.customer_id == user_id
        is_handler = complaint.handled_by == user_id
        is_admin = session.get("role") == "admin"
        
        if not (is_customer or is_handler or is_admin):
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get or create conversation for this complaint
        conversation = session_db.scalar(
            select(Conversation).where(Conversation.complaint_id == complaint_id)
        )
        
        if not conversation:
            conversation = Conversation(complaint_id=complaint_id)
            session_db.add(conversation)
            session_db.flush()
            
            # Add participants
            session_db.add(ChatParticipant(conversation_id=conversation.conversation_id, user_id=complaint.customer_id))
            if complaint.handled_by:
                session_db.add(ChatParticipant(conversation_id=conversation.conversation_id, user_id=complaint.handled_by))
        
        # Create and save message
        new_message = Message(
            conversation_id=conversation.conversation_id,
            sender_id=user_id,
            message_text=message_text,
            related_complaint_id=complaint_id,
        )
        session_db.add(new_message)
        session_db.commit()
        
        return jsonify({
            "success": True,
            "message_id": new_message.message_id,
            "sent_at": new_message.sent_at.isoformat(),
        })


@chat_bp.route("/active-complaints", methods=["GET"])
def get_active_complaints():
    """Get active complaints for the current user"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user_id"]
    role = session.get("role")
    
    if role != "customer":
        return jsonify({"error": "Unauthorized"}), 403
    
    with Session(engine) as session_db:
        complaints = session_db.scalars(
            select(Complaint).where(
                Complaint.customer_id == user_id,
                Complaint.status.notin_(["complete", "rejected"])
            )
        ).all()
        
        active_complaints = [c.complaint_id for c in complaints]
        return jsonify(active_complaints)
