from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.collaboration import CommentCreate, CommentUpdate, CommentResponse
from ...services.comment_service import CommentService

router = APIRouter()

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a dashboard or query
    Supports @mentions for user notifications
    """
    try:
        result = CommentService.create_comment(
            db=db,
            user_id=current_user.id,
            content=comment.content,
            dashboard_id=comment.dashboard_id,
            query_id=comment.query_id,
            parent_id=comment.parent_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )

@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    dashboard_id: Optional[str] = None,
    query_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comments for a dashboard or query
    """
    comments = CommentService.get_comments(
        db=db,
        dashboard_id=dashboard_id,
        query_id=query_id,
        parent_id=parent_id
    )
    return comments

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    update_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a comment (only by owner)
    """
    result = CommentService.update_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
        content=update_data.content
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit it"
        )
    
    return result

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment (only by owner)
    """
    success = CommentService.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    
    return None