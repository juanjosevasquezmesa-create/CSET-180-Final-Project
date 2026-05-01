# Admin dashboard with complaints, warranties, and vendor verification

from flask import Blueprint, render_template, request, redirect, session, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, Complaint, OrderItem, Product, engine

admin_account_bp = Blueprint("admin_account", __name__, url_prefix="/account/")


@admin_account_bp.route("admin", methods=["GET"])
def admin_account():
    """Dashboard with dynamic views based on ?view parameter"""
    if not session or session.get("role") != "admin":
        return redirect(url_for("login.login_page"))
    
    view = request.args.get("view", "dashboard")
    
    try:
        with Session(engine) as session_db:
            # Get counts
            total_complaints = session_db.query(Complaint).count()
            total_warranties = session_db.query(Complaint).filter(
                Complaint.demand == "warranty_claim"
            ).count()
            total_pending_vendors = session_db.query(User).filter(
                User.role == "vendor",
                User.isVerified == "pending"
            ).count()
            
            context = {
                "total_complaints": total_complaints,
                "total_warranties": total_warranties,
                "total_pending_vendors": total_pending_vendors,
                "current_view": view
            }
            
            # Load view-specific data
            if view == "complaints":
                complaints = session_db.execute(
                    select(Complaint, User, OrderItem, Product)
                    .join(User, Complaint.customer_id == User.user_id)
                    .join(OrderItem, Complaint.order_item_id == OrderItem.order_item_id)
                    .join(Product, OrderItem.var_id == Product.product_id)
                    .order_by(Complaint.status, Complaint.complaint_id.desc())
                ).all()
                
                complaint_data = []
                for complaint, customer, order_item, product in complaints:
                    complaint_info = {
                        "complaint": complaint,
                        "customer": customer,
                        "order_item": order_item,
                        "product": product,
                        "handler": complaint.handler if complaint.handled_by else None
                    }
                    complaint_data.append(complaint_info)
                
                context["complaints"] = complaint_data
            
            elif view == "warranty":
                warranty_complaints = session_db.execute(
                    select(Complaint, User, OrderItem, Product)
                    .join(User, Complaint.customer_id == User.user_id)
                    .join(OrderItem, Complaint.order_item_id == OrderItem.order_item_id)
                    .join(Product, OrderItem.var_id == Product.product_id)
                    .where(Complaint.demand == "warranty_claim")
                    .order_by(Complaint.status, Complaint.complaint_id.desc())
                ).all()
                
                warranty_data = []
                for complaint, customer, order_item, product in warranty_complaints:
                    warranty_info = {
                        "complaint": complaint,
                        "customer": customer,
                        "order_item": order_item,
                        "product": product,
                        "handler": complaint.handler if complaint.handled_by else None
                    }
                    warranty_data.append(warranty_info)
                
                context["warranties"] = warranty_data
            
            elif view == "vendors":
                all_vendors = session_db.scalars(
                    select(User).where(User.role == "vendor")
                    .order_by(User.isVerified.asc(), User.user_id.desc())
                ).all()
                
                pending_vendors = [v for v in all_vendors if v.isVerified == "pending"]
                verified_vendors = [v for v in all_vendors if v.isVerified == "verified"]
                
                context["pending_vendors"] = pending_vendors
                context["verified_vendors"] = verified_vendors
                context["total_verified"] = len(verified_vendors)
            
            return render_template("admin_account.html", **context)
    
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "orig"):
            error_msg = e.orig.args[1] if len(e.orig.args) > 1 else str(e.orig)
        print(f"Error loading admin dashboard: {error_msg}")
        return render_template("admin_account.html", error=error_msg)


@aAccount_bp.route("admin/complaint/<int:complaint_id>/update-status", methods=["POST"])
def update_complaint_status(complaint_id):
    """Update complaint status and assign handler"""
    if not session or session.get("role") != "admin":
        return redirect(url_for("login.login_page"))
    
    new_status = request.form.get("status")
    
    try:
        with Session(engine) as session_db:
            complaint = session_db.get(Complaint, complaint_id)
            
            if not complaint:
                return redirect(url_for("admin_account.admin_account", view="complaints", error="Complaint not found"))
            
            complaint.status = new_status
            
            if new_status in ["confirmed", "processing", "complete"] and not complaint.handled_by:
                complaint.handled_by = session.get("userID")
            
            session_db.commit()
            return redirect(url_for("admin_account.admin_account", view="complaints", success=f"Complaint updated to {new_status}"))
    
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "orig"):
            error_msg = e.orig.args[1] if len(e.orig.args) > 1 else str(e.orig)
        print(f"Error updating complaint {complaint_id}: {error_msg}")
        return redirect(url_for("admin_account.admin_account", view="complaints", error=error_msg))


@admin_account_bp.route("admin/vendor/<int:vendor_id>/verify", methods=["POST"])
def verify_vendor(vendor_id):
    """Toggle vendor verification status"""
    if not session or session.get("role") != "admin":
        return redirect(url_for("login.login_page"))
    
    try:
        with Session(engine) as session_db:
            vendor = session_db.get(User, vendor_id)
            
            if not vendor:
                return redirect(url_for("admin_account.admin_account", view="vendors", error="Vendor not found"))
            
            if vendor.role != "vendor":
                return redirect(url_for("admin_account.admin_account", view="vendors", error="User is not a vendor"))
            
            vendor.isVerified = "verified" if vendor.isVerified == "pending" else "pending"
            
            session_db.commit()
            
            status_msg = "verified" if vendor.isVerified == "verified" else "set to pending"
            return redirect(url_for("admin_account.admin_account", view="vendors", success=f"Vendor {status_msg} successfully"))
    
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "orig"):
            error_msg = e.orig.args[1] if len(e.orig.args) > 1 else str(e.orig)
        print(f"Error verifying vendor {vendor_id}: {error_msg}")
        return redirect(url_for("admin_account.admin_account", view="vendors", error=error_msg))
