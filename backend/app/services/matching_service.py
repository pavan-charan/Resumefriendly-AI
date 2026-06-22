import os
from typing import Dict, List, Any
import chromadb
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class MatchingService:
    _model = None

    @classmethod
    def get_model(cls):
        """
        Lazy-loads the Sentence Transformer model to speed up application startup.
        """
        if cls._model is None:
            # Load standard lightweight model
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    def __init__(self):
        # Establish connection to ChromaDB client with exception resilience
        try:
            # Try connecting to the HTTP client (defined in docker-compose)
            self.chroma_client = chromadb.HttpClient(
                host=settings.CHROMADB_HOST,
                port=settings.CHROMADB_PORT
            )
            # Ping client to ensure connection works
            self.chroma_client.heartbeat()
        except Exception:
            # Fallback to local ephemeral client if server isn't up
            self.chroma_client = chromadb.Client()

        # Get or create the vector collection for Resumes
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="resumes_collection"
            )
        except Exception:
            self.collection = None

    def generate_embedding(self, text: str) -> List[float]:
        """
        Encodes target text to a 384-dimensional vector.
        """
        model = self.get_model()
        embedding = model.encode(text)
        return embedding.tolist()

    def add_resume_to_vector_store(self, resume_id: str, text: str, metadata: dict):
        """
        Saves resume text and generated vector into ChromaDB.
        """
        if self.collection is None:
            return
        
        embedding = self.generate_embedding(text)
        self.collection.add(
            ids=[resume_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )

    def match_resume_to_jd(self, resume_text: str, resume_skills: List[str], jd_text: str) -> Dict[str, Any]:
        """
        Calculates cosine similarity matching and maps skill overlaps.
        """
        # Embed text fields
        model = self.get_model()
        embeddings = model.encode([resume_text, jd_text])
        
        # Simple Python Cosine Similarity to avoid numpy overhead
        v1, v2 = embeddings[0], embeddings[1]
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = sum(a * a for a in v1) ** 0.5
        norm_v2 = sum(a * a for a in v2) ** 0.5
        
        similarity = 0.0
        if norm_v1 > 0 and norm_v2 > 0:
            similarity = dot_product / (norm_v1 * norm_v2)
            
        # Convert to percentage
        match_score = int(max(0.0, min(1.0, similarity)) * 100)

        # Heuristic Skills matching (exact overlap check)
        matched_skills = []
        missing_skills = []
        
        # Check standard skills against the Job Description
        from app.services.parser_service import ParserService
        for skill in ParserService.SKILLS_DATABASE:
            skill_lower = skill.lower()
            in_resume = any(skill_lower == rs.lower() for rs in resume_skills)
            in_jd = skill_lower in jd_text.lower()
            
            if in_jd:
                if in_resume:
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)

        # Generate recommendations
        recommendations = []
        for missing in missing_skills[:4]:
            recommendations.append(f"Incorporate direct experience with '{missing}' in your profile.")
        if match_score < 70:
            recommendations.append("Align the wording of your professional accomplishments with keywords in the job description.")
        else:
            recommendations.append("Your profile is strong. Customize project descriptions to highlight matching achievements.")

        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations
        }
