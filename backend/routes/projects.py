from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from database import get_db
from models.project import ProjectCreate, ProjectResponse, Project
from models.user import User
from auth.auth import auth_required
from typing import Optional

router = APIRouter()

@router.post("/projects/", response_model=ProjectResponse)
@auth_required
# TODO: Resolve the type: ignore properly later
def create_project(project: ProjectCreate, request: Request = None, db: Session = Depends(get_db), user_email: Optional[str] = None): # type: ignore
    owner = db.query(User).filter(User.email == user_email).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    
    existing_project = db.query(Project).filter(Project.name == project.name).first()
    if existing_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project name already exists")

    try:
        new_project = Project(
            name=project.name,
            description=project.description,
            owner_id=owner.id  # Use DB id of logged in user (from cookie)
        )
    
        # Transaction
        db.add(new_project)
        db.commit() 
        db.refresh(new_project)
    
    # TODO: Add logger later, send e to Rollbar/Sentry
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating project: {e}")
    
    return ProjectResponse(
        project_id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        owner_id=new_project.owner_id,
        is_active=new_project.is_active
    )