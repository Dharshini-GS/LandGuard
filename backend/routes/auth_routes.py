"""
Authentication Endpoints for LANDGUARD AI.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
import uuid

from backend.database import execute_query_one, execute_write
from backend.auth import verify_password, create_access_token, get_current_user
from backend.schemas import LoginRequest, TokenResponse, UserResponse
from backend.services.audit_service import log_action

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    username = req.username.strip()
    password = req.password.strip()

    user = execute_query_one("SELECT * FROM users WHERE username = ?", (username,))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    login_id = f"LGH-{uuid.uuid4().hex[:10].upper()}"

    if not user or not verify_password(password, user["password_hash"]):
        # Record failed login
        execute_write("""
        INSERT INTO login_history (login_id, username, success_flag, ip_address, timestamp, details)
        VALUES (?, ?, 0, '127.0.0.1', ?, 'Invalid credentials')
        """, (login_id, username, timestamp))

        # Security requirement: friendly generic error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Please try again."
        )

    if user["status"] != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated.")

    # Record successful login
    execute_write("""
    INSERT INTO login_history (login_id, username, success_flag, ip_address, timestamp, details)
    VALUES (?, ?, 1, '127.0.0.1', ?, 'Successful login')
    """, (login_id, username, timestamp))

    execute_write("UPDATE users SET last_login = ? WHERE user_id = ?", (timestamp, user["user_id"]))

    token = create_access_token(data={"sub": user["username"]})
    log_action(user, "LOGIN", details=f"User {user['username']} logged in successfully.")

    user_resp = UserResponse(
        user_id=user["user_id"],
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        scope_type=user["scope_type"],
        state_code=user["state_code"] or "",
        state_name=user["state_name"] or "",
        district_code=user["district_code"] or "",
        district_name=user["district_name"] or "",
        assigned_project_ids=user["assigned_project_ids"] or "",
        status=user["status"]
    )

    return TokenResponse(access_token=token, user=user_resp)

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    log_action(current_user, "LOGOUT", details="User logged out.")
    return {"message": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        scope_type=current_user["scope_type"],
        state_code=current_user["state_code"] or "",
        state_name=current_user["state_name"] or "",
        district_code=current_user["district_code"] or "",
        district_name=current_user["district_name"] or "",
        assigned_project_ids=current_user["assigned_project_ids"] or "",
        status=current_user["status"]
    )
