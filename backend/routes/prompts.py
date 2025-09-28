from fastapi import APIRouter, Body, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models.prompt import PromptCreate, PromptResponse, Prompt, PromptRun, PromptRunResponse, SendPromptRequest, SendPromptResponse
from models.project import Project
from auth.auth import get_current_user
from models.user import User
from models.file import ProjectFile
from llm_client import generate_project_name
from config import openai_client
import uuid
import sentry_sdk
from fastapi.responses import StreamingResponse
import json

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
            model="gpt-4-turbo",     
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

@router.post("/projects/{project_id}/send_prompt", response_model=SendPromptResponse)
def send_project_message(project_id: uuid.UUID, payload: SendPromptRequest = Body(...), db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    # Get prompt_id from request body
    prompt_id = payload.prompt_id
    if not prompt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="prompt_id is required"
        )

    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Verify user access
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Fetch the prompt
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.project_id == project.id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    # Create a PromptRun entry
    run_entry = PromptRun(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        project_id=project.id,
        user_id=user.id,
        status="pending",
        output_data=None
    )
    db.add(run_entry)
    db.commit()
    db.refresh(run_entry)

    # Attach project files if any
    project_files = db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all()
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
                continue

    # Combine prompt content with project files
    full_prompt = prompt.content + ("\n" + file_contents if file_contents else "")

    # Call OpenAI API
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        reply = response.choices[0].message.content
        if reply is None:
            reply = ""
        run_entry.output_data = reply
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

    return SendPromptResponse(
        reply=reply,
        run_id=run_entry.id,
        status=run_entry.status,
        created_at=run_entry.created_at,
        updated_at=run_entry.updated_at
    )
    
@router.post("/projects/{project_id}/messages", response_model=SendPromptResponse)
def send_message(project_id: uuid.UUID, payload: dict = Body(...), db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content is required")

    # Create a new prompt for this message
    prompt = Prompt(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Chat message",
        content=content
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    # Create a run entry
    run_entry = PromptRun(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        project_id=project.id,
        user_id=user.id,
        status="pending",
        input_data=content
    )
    db.add(run_entry)
    db.commit()
    db.refresh(run_entry)

    # Fetch project files if needed
    file_contents = ""
    project_files = db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all()
    for f in project_files:
        if f.file_id:
            try:
                fc = openai_client.files.content(f.file_id)
                if isinstance(fc, bytes):
                    fc = fc.decode("utf-8")
                elif not isinstance(fc, str):
                    fc = str(fc)
                file_contents += fc + "\n"
            except Exception as e:
                sentry_sdk.capture_exception(e)
                continue

    # Combine user message with project files
    full_prompt = content + ("\n" + file_contents if file_contents else "")

    # Call OpenAI API
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        reply = response.choices[0].message.content or ""
        run_entry.output_data = reply
        run_entry.status = "completed"
        db.commit()
        db.refresh(run_entry)
    except Exception as e:
        run_entry.status = "failed"
        db.commit()
        db.refresh(run_entry)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate response")

    return SendPromptResponse(
        reply=reply,
        run_id=run_entry.id,
        status=run_entry.status,
        created_at=run_entry.created_at,
        updated_at=run_entry.updated_at
    )
    
@router.get("/projects/{project_id}/messages")
def get_project_messages(project_id: uuid.UUID, db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    runs = db.query(PromptRun).filter(PromptRun.project_id == project.id).all()
    messages = []
    for run in runs:
        if run.input_data:
            messages.append({
                "id": run.id,
                "role": "user",
                "content": run.input_data
            })
        if run.output_data:
            messages.append({
                "id": run.id,
                "role": "assistant",
                "content": run.output_data
            })
    return messages

@router.post("/projects/{project_id}/generate_name")
def generate_name(project_id: uuid.UUID, payload: dict, db: Session = Depends(get_db)):
    # Find project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    messages = payload.get("messages", [])
    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No messages provided")

    # Call LLM helper
    new_name = generate_project_name(messages)
    project.name = new_name
    db.commit()
    db.refresh(project)

    return {"id": str(project.id), "name": project.name}

# TODO: SSE Streaming works but figure out how to display properly in the frontend
@router.get("/projects/{project_id}/messages/stream")
async def stream_message(project_id: uuid.UUID, content: str = Query(...), db: Session = Depends(get_db), user_email: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Save prompt & run
    prompt = Prompt(id=uuid.uuid4(), project_id=project.id, name="Chat message", content=content)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    run_entry = PromptRun(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        project_id=project.id,
        user_id=user.id,
        status="pending",
        input_data=content
    )
    db.add(run_entry)
    db.commit()
    db.refresh(run_entry)

    # Collect file contents
    file_contents = ""
    for f in db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all():
        if f.file_id:
            try:
                fc = openai_client.files.content(f.file_id)
                if isinstance(fc, bytes):
                    fc = fc.decode("utf-8")
                file_contents += str(fc) + "\n"
            except Exception:
                continue

    full_prompt = content + ("\n" + file_contents if file_contents else "")

    async def event_generator():
        assistant_content = ""
        try:
            # Keep your current pattern: call create(..., stream=True) and iterate
            completion = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )

            for chunk in completion:
                try:
                    choice = chunk.choices[0]
                except Exception:
                    continue

                # robustly extract delta
                delta = None
                if isinstance(choice, dict):
                    delta = choice.get("delta")
                else:
                    delta = getattr(choice, "delta", None)

                # robustly extract content piece
                content_piece = None
                if isinstance(delta, dict):
                    content_piece = delta.get("content")
                else:
                    content_piece = getattr(delta, "content", None)

                if content_piece:
                    assistant_content += content_piece
                    # send only the new delta to the client
                    payload = {"role": "assistant", "delta": content_piece}
                    yield f"data: {json.dumps(payload)}\n\n"

            # stream finished - persist final output and signal client
            run_entry.output_data = assistant_content
            run_entry.status = "completed"
            db.commit()

            # send a custom end event so frontend can close the EventSource & run post-stream logic
            yield "event: end\ndata: {}\n\n"

        except Exception as e:
            # mark failed and return an error delta + end event
            run_entry.status = "failed"
            db.commit()
            sentry_sdk.capture_exception(e)
            yield f"data: {json.dumps({'role':'assistant','delta':'[Error generating response]'})}\n\n"
            yield "event: end\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
