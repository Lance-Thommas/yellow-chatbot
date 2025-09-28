from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy.orm import Session
from database import get_db
from models.project import ProjectCreate, ProjectResponse, Project
from models.user import User
from auth.auth import get_current_user
import sentry_sdk

router = APIRouter()

@router.post("/projects/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
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
    
    except Exception as e:
        db.rollback()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create project")
    
    return new_project

@router.get("/projects/", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    return projects

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str = Path(..., description="ID of the project"), db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project