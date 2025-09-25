from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models.prompt import PromptCreate, PromptResponse, Prompt, PromptRun, PromptRunResponse
from models.project import Project
from auth.auth import get_current_user
from models.user import User
from models.file import ProjectFile
from config import openai_client
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

# TODO: Create ORM model for storing prompt run history/logs later
@router.post("/prompts/{prompt_id}/run", response_model=PromptRunResponse)
def run_prompt(prompt_id: uuid.UUID, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    project = db.query(Project).filter(Project.id == db_prompt.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to run this prompt")

    run_entry = PromptRun(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        project_id=project.id,
        user_id=user.id,
        status="pending"
    )
    db.add(run_entry)
    db.commit()
    db.refresh(run_entry)

    # TODO: Change to specific access file as needed
    # Upload project files to OpenAI if missing file_id
    try:
        project_files = db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all()
        for f in project_files:
            if not f.file_id:
                try:
                    with open(f.local_path, "rb") as file_obj:
                        uploaded = openai_client.files.create(
                            file=file_obj,
                            purpose="assistants"
                        )
                        f.file_id = uploaded.id
                        db.commit()
                        db.refresh(f)
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    continue  # skip failed uploads

        # Retrieve contents of all project files
        file_contents = ""
        for f in project_files:
            if f.file_id:
                try:
                    content = openai_client.files.content(f.file_id)
                    if isinstance(content, bytes):
                        content = content.decode("utf-8")
                    elif not isinstance(content, str):
                        content = str(content)
                    file_contents += content + "\n"
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    continue  # skip failed retrievals

        # Combine prompt content with file contents
        full_prompt_content = db_prompt.content + "\n" + file_contents if file_contents else db_prompt.content
    except Exception as e_fallback:
        sentry_sdk.capture_exception(e_fallback)
        full_prompt_content = db_prompt.content  # fallback to just prompt content

    # Call OpenAI API to run the prompt
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",     
            messages=[{"role": "user", "content": full_prompt_content}],
        )

        output = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage is not None else None
        # TODO: Use actual pricing model based on model used
        cost = (tokens / 1000) * 0.03 if tokens else 0.0  # example cost

        run_entry.output_data = output
        run_entry.tokens_used = tokens
        run_entry.cost = cost
        run_entry.status = "completed"
        db.commit()
        db.refresh(run_entry)

    except Exception as e:
        run_entry.status = "failed"
        db.commit()
        db.refresh(run_entry)
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run prompt via OpenAI API"
        )

    return run_entry


# basic project-level analytics, expand later for per-user or time-based analytics
# TODO: check response model later
@router.get("/analytics/projects/{project_id}/")
def project_analytics(project_id: uuid.UUID, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if user_email matches project owner_id for access control
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    runs = db.query(PromptRun).filter(PromptRun.project_id == project_id).all()
    
    total_tokens = sum(run.tokens_used or 0 for run in runs)
    total_cost = sum(run.cost or 0.0 for run in runs)
    total_runs = len(runs)
    completed_runs = sum(1 for run in runs if run.status == "completed")
    failed_runs = sum(1 for run in runs if run.status == "failed")
    
    return {
        "total_runs": total_runs,
        "completed_runs": completed_runs,
        "failed_runs": failed_runs,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "runs": runs
    }