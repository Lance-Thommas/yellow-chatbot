from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from models.file import ProjectFile
from models.user import User
from auth.auth import get_current_user
from config import openai_client
import uuid
import sentry_sdk

router = APIRouter()

@router.post("/projects/{project_id}/files")
def upload_file(project_id: uuid.UUID, uploaded_file: UploadFile = File(...), db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    # Verify project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(404, "User not found")
    if project.owner_id != user.id:
        raise HTTPException(403, "Not authorized")

    # Upload to OpenAI Files API
    try:
        response = openai_client.files.create(
            file=uploaded_file.file,
            purpose="assistants"
        )
        file_id = response.id

        # Save in DB
        new_file = ProjectFile(
            id=uuid.uuid4(),
            project_id=project_id,
            filename=uploaded_file.filename,
            file_id=file_id,
            purpose="answers"
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {
            "filename": new_file.filename,
            "file_id": new_file.file_id,
            "purpose": new_file.purpose,
            "created_at": new_file.created_at
        }

    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(500, f"Failed to upload file: {e}")
