#This file handles creating, viewing and deactivating admin accounts.

import storage.state as state
from utils.helpers import hash_password, current_timestamp
from utils.logger import audit_logger
from storage.store import save_data


def create_admin(form_data: dict, created_by: str):
    #Create a new admin account.
    username  = form_data["username"]
    full_name = form_data["full_name"]
    email     = form_data["email"]
    password  = form_data["password"]
    role      = form_data["role"]

    # Check that the username is not already taken
    for admin_id, admin in state.admins.items():
        if admin["username"] == username:
            return False, "Username already exists."

    valid_roles = ["super_admin", "election_officer", "station_manager", "auditor"]
    if role not in valid_roles:
        return False, "Invalid role selected."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    state.admins[state.admin_id_counter] = {
        "id":         state.admin_id_counter,
        "username":   username,
        "password":   hash_password(password),
        "full_name":  full_name,
        "email":      email,
        "role":       role,
        "created_at": current_timestamp(),
        "is_active":  True,
    }

    audit_logger.log(
        "CREATE_ADMIN", created_by,
        f"Created admin: {username} (Role: {role})"
    )

    state.admin_id_counter += 1
    save_data()
    return True, f"Admin '{username}' created with role: {role}"


def get_all_admins() -> dict:
    return state.admins


def deactivate_admin(admin_id: int, deactivated_by_id: int, deactivated_by_username: str):
    #Deactivate an admin account by ID.
    if admin_id not in state.admins:
        return False, "Admin not found."

    # Prevent self-deactivation
    if admin_id == deactivated_by_id:
        return False, "You cannot deactivate your own account."

    state.admins[admin_id]["is_active"] = False
    admin_username = state.admins[admin_id]["username"]

    audit_logger.log(
        "DEACTIVATE_ADMIN", deactivated_by_username,
        f"Deactivated admin: {admin_username}"
    )
    save_data()
    return True, f"Admin '{admin_username}' has been deactivated."