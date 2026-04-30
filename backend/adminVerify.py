from flask import Blueprint, session, jsonify, request, abort
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from .models import Complaint, Message, Conversation, ChatParticipant, User, engine

verify_bp = Blueprint("adminVerify", __name__, url_prefix="/verify/<int:user_id>")

@verify_bp.route("", methods=['POST'])
def verify_user(user_id):
    
    if not session.get('isAdmin'):
        abort(403)
    
    try:
        with Session(engine) as session_db:
            user = session_db.get(User, user_id)
            
            if not user:
                pass #add some error saying that user not found
                # return redirect(url_for('all_accounts', error='User not found'))
            
            # Prevent admin from modifying their own verification status
            if user.role == "admin" and session.get('userID') == user_id:
                pass #add some error saying admin cannot change their own accoutn
                # return redirect(url_for('all_accounts', error='Cannot modify your own verification status'))
            
            # Toggle verification status
            user.isVerified = not user.isVerified
            
            session_db.commit()
            
            # success_message = f"User {'verified' if user.isVerified else 'unverified'} successfully"
            return # redirect the admin to the all accounts page # redirect(url_for('all_accounts', success=success_message))
            
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "orig"):
            error_msg = e.orig.args[1] if len(e.orig.args) > 1 else str(e.orig)
        
        print(f"Error verifying user {user_id}: {error_msg}")
        return # redirect the admin to the all accounts page # redirect(url_for('all_accounts', error=error_msg))    