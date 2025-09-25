from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models.prompt import PromptCreate, PromptResponse, Prompt
from models.project import Project
from auth.auth import get_current_user
from models.user import User
import uuid
import sentry_sdk

router = APIRouter()

@router.post("/prompts/", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    # Verify project exists
    project = db.query(Project).filter(Project.id == prompt.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    try:
        new_prompt = Prompt(
            id=uuid.uuid4(),
            project_id=prompt.project_id,
            name=prompt.name,
            description=prompt.description,
            content=prompt.content
        )
        
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
    
    except Exception as e:
        db.rollback()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create prompt")
    
    return new_prompt

@router.get("/projects/{project_id}/prompts", response_model=list[PromptResponse])
def get_prompts_by_project(project_id: uuid.UUID, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if user_email matches project owner_id for access control
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project's prompts")

    prompts = db.query(Prompt).filter(Prompt.project_id == project_id).all()
    return prompts

@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: uuid.UUID, prompt: PromptCreate, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == prompt.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check if user_email matches project owner_id for access control
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this prompt")
    
    try:
        db_prompt.project_id = prompt.project_id
        db_prompt.name = prompt.name
        db_prompt.description = prompt.description
        db_prompt.content = prompt.content
        
        db.commit()
        db.refresh(db_prompt)
    
    except Exception as e:
        db.rollback()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update prompt")
    
    return db_prompt

@router.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: uuid.UUID, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == db_prompt.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check if user_email matches project owner_id for access control
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this prompt")
    
    try:
        db.delete(db_prompt)
        db.commit()
    except Exception as e:
        db.rollback()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete prompt")
    
    return

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id: uuid.UUID, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    # Verify project exists
    project = db.query(Project).filter(Project.id == db_prompt.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if user_email matches project owner_id for access control
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this prompt")

    return db_prompt
