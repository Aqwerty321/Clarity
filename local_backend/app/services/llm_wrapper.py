"""
LLM Wrapper with multiple provider support (mock, gpt-oss, gemini, openai)
"""
import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get model name"""
        pass


class MockLLM(LLMInterface):
    """Mock LLM for testing and demo"""
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Return a hardcoded response"""
        
        # Simple keyword-based responses
        prompt_lower = prompt.lower()
        
        if "neural network" in prompt_lower or "nn" in prompt_lower:
            return (
                "Neural networks are computational models inspired by biological neural networks. "
                "They consist of interconnected nodes (neurons) organized in layers. "
                "Each connection has a weight that adjusts during training. "
                "The network learns by adjusting these weights to minimize prediction errors through backpropagation."
            )
        
        elif "gradient descent" in prompt_lower:
            return (
                "Gradient descent is an optimization algorithm used to minimize the loss function in machine learning. "
                "It works by iteratively adjusting parameters in the direction opposite to the gradient of the loss function. "
                "The learning rate controls the size of each step."
            )
        
        elif "quiz" in prompt_lower:
            return """Question 1: What are neural networks inspired by?
A) Computer algorithms
B) Biological neural networks
C) Mathematical equations
D) Physical processes

Question 2: What adjusts during neural network training?
A) The number of layers
B) The activation functions
C) The connection weights
D) The input data

Question 3: What is backpropagation used for?
A) Forward pass computation
B) Data preprocessing
C) Calculating gradients for weight updates
D) Model evaluation"""
        
        else:
            return (
                "Based on the provided context, I can help answer your question. "
                "However, this is a mock LLM response. "
                "Please configure a real LLM provider (gpt-oss, gemini, or openai) for production use."
            )
    
    def get_model_name(self) -> str:
        return "mock-llm-v1"


class GPTOSSAdapter(LLMInterface):
    """Adapter for gpt-oss via Ollama (local inference)"""
    
    def __init__(self, model_name: str = None):
        # Get model name from env if not provided
        if model_name is None:
            model_name = os.getenv("LLM_MODEL", "gpt-oss:20b")
        self.model_name = model_name
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Test Ollama connection
        try:
            import requests
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.use_ollama = True
                logger.info(f"✅ Using Ollama for LLM: {self.model_name}")
            else:
                raise ConnectionError("Ollama not responding")
        except Exception as e:
            logger.warning(f"Ollama not available ({e}), falling back to mock")
            self.use_ollama = False
            self.mock = MockLLM()
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        if not self.use_ollama:
            return self.mock.generate(prompt, max_tokens, temperature, **kwargs)
        
        # Use Ollama API
        try:
            import requests
            # Use longer timeout for longer generations
            timeout = kwargs.get('timeout', 120)
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            # Fallback to mock
            if not hasattr(self, 'mock'):
                self.mock = MockLLM()
            return self.mock.generate(prompt, max_tokens, temperature, **kwargs)
    
    def get_model_name(self) -> str:
        return self.model_name


class GeminiAdapter(LLMInterface):
    """Adapter for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # TODO: Initialize Gemini client
        logger.warning("Gemini not implemented, using mock responses")
        self.mock = MockLLM()
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        # TODO: Implement Gemini API call
        return self.mock.generate(prompt, max_tokens, temperature, **kwargs)
    
    def get_model_name(self) -> str:
        return "gemini-pro"


class OpenAIAdapter(LLMInterface):
    """Adapter for OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        # TODO: Initialize OpenAI client
        logger.warning("OpenAI not implemented, using mock responses")
        self.mock = MockLLM()
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        # TODO: Implement OpenAI API call
        return self.mock.generate(prompt, max_tokens, temperature, **kwargs)
    
    def get_model_name(self) -> str:
        return self.model


class LLMWrapper:
    """Unified LLM wrapper that selects provider based on config"""
    
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "mock").lower()
        model_name = os.getenv("LLM_MODEL", "gpt-oss:20b")
        
        if provider == "mock":
            self.llm = MockLLM()
        elif provider in ["gpt-oss", "ollama"]:
            self.llm = GPTOSSAdapter(model_name=model_name)
        elif provider == "gemini":
            self.llm = GeminiAdapter()
        elif provider == "openai":
            self.llm = OpenAIAdapter(model=model_name)
        else:
            logger.warning(f"Unknown LLM provider: {provider}, using mock")
            self.llm = MockLLM()
        
        logger.info(f"Initialized LLM: {self.llm.get_model_name()}")
    
    def build_rag_prompt(
        self,
        question: str,
        context_chunks: List[str],
        include_instructions: bool = True
    ) -> str:
        """Build RAG prompt with context"""
        
        context = "\n\n".join([
            f"[Excerpt {i+1}]:\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        if include_instructions:
            prompt = f"""SYSTEM: You are Clarity, an educational assistant. Use the provided document excerpts to answer concisely. If unsure, say "I don't know" and suggest searching or uploading more material.

CONTEXT:
{context}

USER: {question}

INSTRUCTIONS:
- Use only facts from CONTEXT.
- Provide short summary (2-3 sentences).
- Be accurate and cite sources when possible."""
        else:
            prompt = f"""Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"""
        
        return prompt
    
    def answer_question(
        self,
        question: str,
        context_chunks: List[str],
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """Generate answer using RAG prompt"""
        
        prompt = self.build_rag_prompt(question, context_chunks)
        return self.llm.generate(prompt, max_tokens, temperature)
    
    def generate_quiz(
        self,
        topic: str,
        context_chunks: List[str],
        difficulty: str = "medium",
        num_questions: int = 5
    ) -> str:
        """Generate quiz questions from context"""
        
        context = "\n\n".join(context_chunks[:3])  # Limit context for quiz gen
        
        prompt = f"""You are a quiz generator. Generate {num_questions} multiple-choice questions about {topic} based on the provided content.

Difficulty level: {difficulty}

Content:
{context}

IMPORTANT: Respond with ONLY valid JSON in this exact format, no additional text:
{{
  "questions": [
    {{
      "question": "Your question here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Why this answer is correct",
      "hint": "A helpful hint without giving away the answer",
      "incorrect_explanations": [
        "Why option A is wrong (or empty if it's the correct answer)",
        "Why option B is wrong (or empty if it's the correct answer)",
        "Why option C is wrong (or empty if it's the correct answer)",
        "Why option D is wrong (or empty if it's the correct answer)"
      ]
    }}
  ]
}}

Rules:
- Generate exactly {num_questions} questions based on the content
- Each question must have exactly 4 options
- correct_answer is the index (0-3) of the correct option
- Provide a helpful hint that guides without revealing the answer
- For incorrect_explanations, explain why each incorrect option is wrong, leave correct answer's explanation empty
- Output ONLY the JSON, no markdown, no code blocks, no extra text"""
        
        return self.llm.generate(prompt, max_tokens=3000, temperature=0.7)
    
    def get_model_name(self) -> str:
        """Get current model name"""
        return self.llm.get_model_name()


# Global instance
llm_wrapper = LLMWrapper()
