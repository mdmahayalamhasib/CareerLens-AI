import os
import torch
import traceback
from typing import Optional, Dict, Any

# Configuration
RELEVANCE_THRESHOLD = 0.50

# Lazy-loaded model instance
_model = None

def get_model_path():
    return os.path.join(os.path.dirname(__file__), 'models', 'mpnet_relevance_finetuned')

def load_relevance_model():
    """Lazy loads the fine-tuned relevance model if not already loaded."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model_path = get_model_path()
            if not os.path.exists(model_path):
                raise RuntimeError(f"Model path does not exist: {model_path}")
                
            # Load on CPU explicitly for predictable isolated inference (unless requested otherwise)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _model = SentenceTransformer(model_path).to(device)
            _model.eval() # Ensure eval mode
        except Exception as e:
            print(f"Failed to load relevance model: {e}")
            traceback.print_exc()
            raise
    return _model

def calculate_relevance(job_requirement: str, resume_context: str) -> Dict[str, Any]:
    """
    Calculates the semantic relevance score between a job requirement and a resume context.
    Returns a dict with the raw score, boolean relevance, and threshold.
    """
    if not job_requirement or not resume_context:
        # Handle empty strings gracefully
        return {
            "relevance_score": 0.0,
            "is_relevant": False,
            "threshold": RELEVANCE_THRESHOLD
        }
        
    try:
        from sentence_transformers import util
        model = load_relevance_model()
        
        # Calculate cosine similarity using sentence-transformers util
        emb1 = model.encode(resume_context, convert_to_tensor=True)
        emb2 = model.encode(job_requirement, convert_to_tensor=True)
        
        sim = util.cos_sim(emb1, emb2).item()
        
        return {
            "relevance_score": float(sim),
            "is_relevant": sim >= RELEVANCE_THRESHOLD,
            "threshold": RELEVANCE_THRESHOLD
        }
    except Exception as e:
        print(f"Inference error: {e}")
        # Fail safe
        return {
            "relevance_score": 0.0,
            "is_relevant": False,
            "threshold": RELEVANCE_THRESHOLD
        }
