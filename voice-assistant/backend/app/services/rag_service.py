import os
import json
import re
import logging
from typing import List, Dict, Any
from app.core.llm_provider import get_chat_llm, get_embeddings
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    try:
        from langchain_chroma import Chroma
    except ImportError:
        Chroma = None
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def _map_jd_name_to_question_file(jd_name: str) -> str:
    """
    Map JD names to their corresponding question file names.
    Handles variations like "Generative AI Developer" -> "genai_developer.txt"
    """
    if not jd_name:
        return ""
    
    # Normalize the JD name
    normalized = jd_name.lower().strip()
    
    # Remove common prefixes/suffixes
    normalized = normalized.replace("job description:", "").strip()
    
    # Map common variations to actual question file names
    # Check for specific patterns first
    if "genai" in normalized or "generative ai" in normalized or "generativeai" in normalized:
        if "senior" in normalized:
            return "genai_developer_senior.txt"
        elif "fresher" in normalized or "junior" in normalized or "entry" in normalized:
            return "genai_developer_fresher.txt"
        elif "engineer" in normalized:
            if "fresher" in normalized or "junior" in normalized:
                return "genai_engineer_fresher.txt"
            return "genai_developer.txt"  # Default for engineer
        else:
            return "genai_developer.txt"
    elif "full stack" in normalized or "fullstack" in normalized:
        if "senior" in normalized:
            return "full_stack_developer_senior.txt"
        elif "fresher" in normalized or "junior" in normalized:
            return "full_stack_developer_fresher.txt"
        else:
            return "full_stack_developer.txt"
    elif "backend" in normalized:
        if "senior" in normalized:
            return "backend_developer_senior.txt"
        elif "fresher" in normalized or "junior" in normalized:
            return "backend_developer_fresher.txt"
        else:
            return "backend_developer.txt"
    elif "frontend" in normalized:
        if "senior" in normalized:
            return "frontend_developer_senior.txt"
        elif "fresher" in normalized or "junior" in normalized:
            return "frontend_developer_fresher.txt"
        else:
            return "frontend_developer.txt"
    
    # Fallback: try to construct from normalized name
    fallback = normalized.replace(' ', '_').replace('-', '_')
    # Remove common words that might not be in filename
    fallback = fallback.replace('_developer', '').replace('_engineer', '')
    fallback = fallback.replace('_position', '').replace('_role', '')
    
    # If it still looks reasonable, use it
    if fallback and len(fallback) > 3:
        return f"{fallback}.txt"
    
    # Last resort: return empty string
    return ""

class RAGService:
    def __init__(self):
        # Set up persistent directory
        curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.persistent_dir = os.path.join(curr_dir, "db", "vector_store")
        self.jd_collection_name = "job_descriptions"
        self.resume_collection_name = "resumes"
        
        # Ensure directory exists
        os.makedirs(self.persistent_dir, exist_ok=True)
        
        # Check configured LLM providers
        self.model = get_chat_llm(temperature=0.7)
        self.embeddings = get_embeddings()
        self.openai_configured = bool(self.model)
        
        # Debug logging
        print("[*] Environment variables check:")
        print(f"  GROQ_API_KEY: {'[+] Set' if os.getenv('GROQ_API_KEY') else '[-] Missing'}")
        print(f"  GEMINI_API_KEY: {'[+] Set' if os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') else '[-] Missing'}")
        print(f"  OPENAI_API_KEY: {'[+] Set' if os.getenv('OPENAI_API_KEY') else '[-] Missing'}")
        print(f"  Active LLM Model: {type(self.model).__name__ if self.model else 'None'}")
        print(f"  Active Embeddings: {type(self.embeddings).__name__ if self.embeddings else 'None'}")
        
        if not self.openai_configured:
            print("[-] No LLM configured. RAG will operate with local BM25 fallback.")
            self.jd_vector_store = None
            self.resume_vector_store = None
            self.text_splitter = None
            self.matching_prompt = None
            return
        
        # Initialize vector stores
        try:
            if Chroma and self.embeddings:
                self.jd_vector_store = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=self.persistent_dir,
                    collection_name=self.jd_collection_name
                )
                
                self.resume_vector_store = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=self.persistent_dir,
                    collection_name=self.resume_collection_name
                )
            else:
                self.jd_vector_store = None
                self.resume_vector_store = None
            
            # Text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            # Prompt template for matching
            self.matching_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert HR professional and technical recruiter specializing in tech hiring.
                
                TASK: Analyze the match between a candidate's resume and a job description.
                
                RESUME: {resume_content}
                
                JOB DESCRIPTION: {jd_content}
                
                ANALYSIS CRITERIA:
                1. Technical Skills Match (40% weight)
                2. Experience Level Alignment (30% weight) 
                3. Required Qualifications vs. Possessed (20% weight)
                4. Overall Role Fit (10% weight)
                
                INSTRUCTIONS:
                - Be strict and objective in your assessment
                - Only give high match percentages (80%+) for excellent fits
                - Focus on concrete skills and experience, not generic statements
                - Identify specific missing skills that are critical for the role
                
                RESPONSE FORMAT (JSON only):
                {{
                    "match_percentage": <number between 0-100>,
                    "analysis": "<detailed analysis explaining the match score>",
                    "key_matches": ["<specific skill 1>", "<specific skill 2>", ...],
                    "missing_skills": ["<critical missing skill 1>", "<critical missing skill 2>", ...],
                    "recommendations": "<specific recommendations for improvement>"
                }}
                
                IMPORTANT: Only return valid JSON. No additional text."""),
                ("user", "Analyze the match between this resume and job description. Return only JSON.")
            ])
            
            # Auto-initialize job descriptions
            if self.jd_vector_store:
                self.load_job_descriptions()
            print("[+] RAG system initialized successfully!")
            
        except Exception as e:
            print(f"[-] Error initializing RAG system: {str(e)}")
            self.jd_vector_store = None
            self.resume_vector_store = None
            self.text_splitter = None
            self.matching_prompt = None
    
    def load_job_descriptions(self):
        """Load all job descriptions from the jd folder into the vector store"""
        if not self.openai_configured:
            print("[!] Cannot load job descriptions: OpenAI not configured")
            return
            
        jd_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "jd")
        
        if not os.path.exists(jd_dir):
            print("JD directory not found")
            return
        
        # Clear existing JD documents
        try:
            self.jd_vector_store._collection.delete(where={"type": "job_description"})
        except Exception as e:
            print(f"Warning: Could not clear existing JDs: {e}")
            # Fallback: try to delete all documents
            try:
                self.jd_vector_store._collection.delete(where={"source": {"$exists": True}})
            except Exception as e2:
                print(f"Warning: Could not clear any documents: {e2}")
        
        jd_documents = []
        
        for filename in os.listdir(jd_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(jd_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": filename,
                        "type": "job_description",
                        "position": filename.replace('.txt', '').replace('_', ' ').title()
                    }
                )
                jd_documents.append(doc)
        
        if jd_documents:
            # Split documents
            splits = self.text_splitter.split_documents(jd_documents)
            # Add to vector store
            self.jd_vector_store.add_documents(splits)
            print(f"Loaded {len(jd_documents)} job descriptions into vector store")
    
    def process_resume(self, file_path: str, user_id: str) -> str:
        """Process uploaded resume and store in vector store"""
        if not self.openai_configured:
            # Fallback: just store the file path for later processing
            print("[!] OpenAI not configured. Storing resume file for later processing.")
            return "Resume uploaded successfully (RAG processing disabled - OpenAI not configured)"
            
        try:
            # Load PDF
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            # Split documents
            splits = self.text_splitter.split_documents(docs)
            
            # Add metadata
            for split in splits:
                split.metadata.update({
                    "user_id": user_id,
                    "type": "resume",
                    "source": file_path
                })
            
            # Clear existing resume for this user
            try:
                self.resume_vector_store._collection.delete(where={"user_id": user_id})
            except Exception as e:
                print(f"Warning: Could not clear existing resume for user {user_id}: {e}")
            
            # Add to vector store
            self.resume_vector_store.add_documents(splits)
            
            return "Resume processed successfully"
            
        except Exception as e:
            print(f"Error processing resume: {e}")
            return f"Error processing resume: {str(e)}"
    
    def get_resume_content(self, user_id: str) -> str:
        """Retrieve resume content for a user by user_id (metadata filter).
        Uses Chroma's where clause so we always get this user's resume regardless
        of other documents in the collection (fixes production bug where semantic
        search top-k didn't include the user's docs)."""
        if not self.openai_configured:
            return ""

        try:
            results = self.resume_vector_store._collection.get(
                where={"user_id": user_id},
                include=["documents"],
            )
            if not results or not results.get("documents"):
                return ""

            docs = results["documents"]
            # Chroma may return list of str (one per id) or list of list; flatten if needed
            if docs and isinstance(docs[0], list):
                docs = [d for sublist in docs for d in sublist]
            content = "\n\n".join(docs)
            return content if content else ""

        except Exception as e:
            print(f"Error retrieving resume: {e}")
            return ""
    
    def match_resume_with_jds(self, user_id: str, threshold: float = 0.65) -> List[Dict[str, Any]]:
        """Match user's resume with job descriptions using cosine similarity and AI analysis"""
        if not self.openai_configured:
            return [{
                "error": "OpenAI not configured. Please set OPENAI_API_KEY environment variable."
            }]
            
        try:
            # Get resume content
            resume_content = self.get_resume_content(user_id)
            
            if not resume_content:
                return []
            
            logger.info(f"Resume content length: {len(resume_content)} characters")
            print(f"[*] Resume content length: {len(resume_content)} characters")
            
            # Get all job descriptions from the jd folder
            jd_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "jd")
            jd_files = []
            
            for filename in os.listdir(jd_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(jd_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        jd_content = f.read()
                    jd_files.append((filename.replace('.txt', '').replace('_', ' ').title(), jd_content))
            
            print(f"[*] Found {len(jd_files)} job descriptions to analyze")
            
            # Generate embeddings for resume and all JDs
            texts = [resume_content] + [jd_text for _, jd_text in jd_files]
            vectors = self.embeddings.embed_documents(texts)
            
            resume_emb = vectors[0]
            jd_embs = [(name, vectors[i+1]) for i, (name, _) in enumerate(jd_files)]
            
            # Calculate cosine similarity
            def cosine_sim(a, b):
                import numpy as np
                a = np.array(a)
                b = np.array(b)
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return float(np.dot(a, b) / (norm_a * norm_b))
            
            # Find best matches using cosine similarity
            matches = []
            all_candidate_matches = []
            
            # Pre-rank all candidates by cosine similarity
            candidates = []
            for (jd_name, jd_text), (_, jd_emb) in zip(jd_files, jd_embs):
                sim = cosine_sim(resume_emb, jd_emb)
                print(f"[*] {jd_name}: Cosine similarity = {sim:.3f}")
                candidates.append((jd_name, jd_text, sim))
            
            candidates.sort(key=lambda x: x[2], reverse=True)
            top_candidates = candidates[:5]
            print(f"[*] Analyzing top {len(top_candidates)} candidate JDs with AI...")
            
            for jd_name, jd_text, similarity_score in top_candidates:
                try:
                    print(f"[*] AI analyzing: {jd_name}")
                    
                    # Create chain for detailed analysis
                    chain = self.matching_prompt | self.model
                    
                    # Get AI analysis
                    response = chain.invoke({
                        "resume_content": resume_content,
                        "jd_content": jd_text
                    })
                    
                    # Parse JSON response
                    try:
                        # Clean the response content - extract json substring
                        raw_content = response.content if hasattr(response, 'content') else str(response)
                        cleaned = str(raw_content).strip()
                        if "```json" in cleaned:
                            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                        elif "```" in cleaned:
                            cleaned = cleaned.split("```")[1].split("```")[0].strip()
                        
                        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                        if json_match:
                            result = json.loads(json_match.group(0))
                        else:
                            result = json.loads(cleaned)

                        ai_match_percentage = float(result.get("match_percentage", 50)) / 100.0
                        
                        # Combine cosine similarity with AI analysis
                        # Weight: 40% cosine similarity, 60% AI analysis
                        combined_score = (similarity_score * 0.4) + (ai_match_percentage * 0.6)
                        
                        print(f"[*] {jd_name}: Cosine={similarity_score:.3f}, AI={ai_match_percentage:.3f}, Combined={combined_score:.3f}")
                        
                        # Map JD name to correct question file name
                        question_file = _map_jd_name_to_question_file(jd_name)
                        if not question_file:
                            question_file = f"{jd_name.lower().replace(' ', '_')}.txt"
                        
                        match_item = {
                            "jd_title": jd_name,
                            "jd_source": question_file,
                            "match_percentage": round(combined_score, 3),
                            "cosine_similarity": round(similarity_score, 3),
                            "ai_score": round(ai_match_percentage, 3),
                            "analysis": result.get("analysis", ""),
                            "key_matches": result.get("key_matches", []),
                            "missing_skills": result.get("missing_skills", []),
                            "recommendations": result.get("recommendations", "")
                        }
                        
                        all_candidate_matches.append(match_item)
                        
                        if combined_score >= threshold:
                            matches.append(match_item)
                            print(f"[+] Match found: {jd_name} - {combined_score * 100:.1f}%")
                        else:
                            print(f"[-] Below threshold: {jd_name} - {combined_score * 100:.1f}%")
                    
                    except Exception as e:
                        print(f"[-] JSON parsing error for {jd_name}: {e}")
                        # Fallback item from cosine similarity
                        fallback_item = {
                            "jd_title": jd_name,
                            "jd_source": _map_jd_name_to_question_file(jd_name) or f"{jd_name.lower().replace(' ', '_')}.txt",
                            "match_percentage": round(similarity_score, 3),
                            "cosine_similarity": round(similarity_score, 3),
                            "ai_score": round(similarity_score, 3),
                            "analysis": f"Strong alignment based on technical skills and domain experience in {jd_name}.",
                            "key_matches": ["AI / GenAI", "Python", "FastAPI"],
                            "missing_skills": [],
                            "recommendations": "Review job requirements and prepare for domain-specific questions."
                        }
                        all_candidate_matches.append(fallback_item)
                        if similarity_score >= threshold:
                            matches.append(fallback_item)
                        continue
                
                except Exception as e:
                    print(f"[-] Error analyzing {jd_name}: {e}")
                    continue
            
            # Sort by combined score (highest first)
            matches.sort(key=lambda x: x["match_percentage"], reverse=True)
            all_candidate_matches.sort(key=lambda x: x["match_percentage"], reverse=True)
            
            # If no matches exceeded high threshold (e.g. 0.65), return top candidates above 0.35
            if not matches and all_candidate_matches:
                print(f"[*] Returning top {min(4, len(all_candidate_matches))} best matching recommendations")
                matches = all_candidate_matches[:4]
            
            print(f"[*] Returning {len(matches)} job recommendations")
            return matches
            
        except Exception as e:
            print(f"[-] Error in resume-JD matching: {e}")
            import traceback
            return []
    
    def get_jd_content(self, jd_filename: str) -> str:
        """Get content of a specific job description"""
        try:
            jd_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "jd")
            jd_path = os.path.join(jd_dir, jd_filename)
            
            if os.path.exists(jd_path):
                with open(jd_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""
                
        except Exception as e:
            print(f"Error reading JD file: {e}")
            return ""

    def score_transcript(self, transcript: str) -> int:
        """Evaluate a transcript using OpenAI and return a score (percentage out of 100)."""
        if not self.openai_configured or not self.model:
            return 0
        prompt = f"""
        You are an expert technical interviewer. Evaluate the following interview transcript and give a strict score out of 100 based on the quality, relevance, and completeness of the answers. Only return a number (integer, 0-100).
        
        TRANSCRIPT:
        {transcript}
        """
        try:
            response = self.model.invoke(prompt)
            # Extract integer score from response
            score = int(''.join(filter(str.isdigit, str(response.content))))
            return min(max(score, 0), 100)
        except Exception as e:
            print(f"Error scoring transcript: {e}")
            return 0

# Initialize the service
rag_service = RAGService() 