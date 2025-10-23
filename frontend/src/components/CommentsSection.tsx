import React, { useState, useEffect } from 'react';
import { MessageCircle, Send, Trash2, Edit2 } from 'lucide-react';
import commentService, { Comment, CreateCommentRequest } from '../services/commentService';

interface CommentsSectionProps {
  dashboardId?: string;
  queryId?: string;
}

const CommentsSection: React.FC<CommentsSectionProps> = ({ dashboardId, queryId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [dashboardId, queryId]);

  const fetchComments = async () => {
    try {
      const data = await commentService.getComments(dashboardId, queryId);
      setComments(data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setLoading(true);
      const request: CreateCommentRequest = {
        content: newComment,
        dashboard_id: dashboardId,
        query_id: queryId
      };
      await commentService.createComment(request);
      setNewComment('');
      fetchComments();
    } catch (error) {
      console.error('Failed to create comment:', error);
      alert('Failed to add comment');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (commentId: string) => {
    if (!window.confirm('Delete this comment?')) return;
    
    try {
      await commentService.deleteComment(commentId);
      setComments(comments.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Failed to delete comment:', error);
      alert('Failed to delete comment');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6" data-testid="comments-section">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <MessageCircle className="h-5 w-5 mr-2" />
        Comments ({comments.length})
      </h3>

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment... (use @ to mention users)"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            data-testid="comment-input"
          />
          <button
            type="submit"
            disabled={loading || !newComment.trim()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            data-testid="submit-comment-btn"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Tip: Use @username to mention users
        </p>
      </form>

      <div className="space-y-4">
        {comments.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No comments yet. Be the first to comment!
          </p>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className="border-l-4 border-indigo-200 pl-4 py-2"
              data-testid={`comment-${comment.id}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{comment.content}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(comment.created_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(comment.id)}
                  className="text-gray-400 hover:text-red-600 ml-2"
                  title="Delete comment"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CommentsSection;
