"""
LLaMA Client for EDITH
Handles local LLaMA model inference using llama-cpp-python, transformers, or Ollama
"""

import logging
from typing import Optional, List, Dict
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LlamaClient:
    """Client for running LLaMA models locally"""
    
    def __init__(
        self,
        model_path: str,
        model_type: str = "gguf",
        use_gpu: bool = True,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ):
        """
        Initialize LLaMA client
        
        Args:
            model_path: Path to the model file, HuggingFace model name, or Ollama model name
            model_type: Type of model - "gguf" for llama-cpp, "transformers" for HF, or "ollama" for Ollama
            use_gpu: Whether to use GPU acceleration
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        self.model_path = model_path
        
        # Auto-detect Ollama format (e.g., "llama3.1:8b-instruct-q4_K_M")
        if ":" in model_path and not model_path.startswith("./") and not model_path.startswith("/"):
            self.model_type = "ollama"
            logger.info("Detected Ollama model format")
        else:
            self.model_type = model_type
            
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = None
        self.tokenizer = None
        
        logger.info(f"Initializing LLaMA client with {self.model_type} backend")
        logger.info(f"Model: {model_path}")
        logger.info(f"GPU available: {torch.cuda.is_available()}, Using GPU: {self.use_gpu}")
        
        self.load_model()
    
    def load_model(self):
        """Load the LLaMA model"""
        try:
            if self.model_type == "ollama":
                self._load_ollama_model()
            elif self.model_type == "gguf":
                self._load_llama_cpp_model()
            elif self.model_type == "transformers":
                self._load_transformers_model()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _load_ollama_model(self):
        """Load model using Ollama"""
        try:
            import requests
            
            # Check if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                response.raise_for_status()
                logger.info("Connected to Ollama")
                
                # Check if model is available
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                
                if self.model_path not in model_names:
                    logger.warning(f"Model {self.model_path} not found in Ollama. Available models: {model_names}")
                    logger.info(f"Attempting to pull model {self.model_path}...")
                    # You might want to pull the model here
                else:
                    logger.info(f"Model {self.model_path} is available in Ollama")
                
                self.model = "ollama"  # Marker that we're using Ollama
                
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Could not connect to Ollama. Is it running? Error: {str(e)}")
                
        except ImportError:
            logger.error("requests library not installed. Install with: pip install requests")
            raise
    
    def _load_llama_cpp_model(self):
        """Load model using llama-cpp-python (for GGUF files)"""
        try:
            from llama_cpp import Llama
            
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # Context window
                n_gpu_layers=-1 if self.use_gpu else 0,  # -1 = use all layers on GPU
                n_threads=4,
                verbose=False
            )
            
            logger.info("Loaded model with llama-cpp-python")
            
        except ImportError:
            logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            raise
    
    def _load_transformers_model(self):
        """Load model using HuggingFace transformers"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            device = "cuda" if self.use_gpu else "cpu"
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.use_gpu else torch.float32,
                device_map="auto" if self.use_gpu else None,
                low_cpu_mem_usage=True
            )
            
            if not self.use_gpu:
                self.model = self.model.to(device)
            
            logger.info(f"Loaded model with transformers on {device}")
            
        except ImportError:
            logger.error("transformers not installed. Install with: pip install transformers")
            raise
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (overrides default)
            temperature: Sampling temperature (overrides default)
            stop_sequences: List of sequences that stop generation
            
        Returns:
            Generated text
        """
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        try:
            if self.model_type == "ollama":
                return self._generate_ollama(prompt, max_tokens, temperature, stop_sequences)
            elif self.model_type == "gguf":
                return self._generate_llama_cpp(prompt, max_tokens, temperature, stop_sequences)
            elif self.model_type == "transformers":
                return self._generate_transformers(prompt, max_tokens, temperature)
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop_sequences: Optional[List[str]]
    ) -> str:
        """Generate using Ollama API"""
        import requests
        import json
        
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model_path,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "stop": stop_sequences or []
                }
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise
    
    def _generate_llama_cpp(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop_sequences: Optional[List[str]]
    ) -> str:
        """Generate using llama-cpp-python"""
        output = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop_sequences or [],
            echo=False
        )
        
        return output['choices'][0]['text']
    
    def _generate_transformers(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using transformers"""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        if self.use_gpu:
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the prompt from the output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
    
    def create_prompt(
        self,
        system_message: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Create a formatted prompt for LLaMA
        Supports both LLaMA 2 and LLaMA 3.1 formats
        
        Args:
            system_message: System instructions
            user_message: User query
            context: Optional context from RAG retrieval
            
        Returns:
            Formatted prompt
        """
        # Check if using LLaMA 3.1 (detect from model path)
        is_llama_3 = "llama3" in self.model_path.lower() or "llama-3" in self.model_path.lower()
        
        if is_llama_3:
            # LLaMA 3.1 format with proper tokens
            if context:
                prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

Context:
{context}

Question: {user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            else:
                prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        else:
            # LLaMA 2 format (original)
            if context:
                prompt = f"""<s>[INST] <<SYS>>
{system_message}
<</SYS>>

Context:
{context}

User: {user_message} [/INST]"""
            else:
                prompt = f"""<s>[INST] <<SYS>>
{system_message}
<</SYS>>

{user_message} [/INST]"""
        
        return prompt
    
    def chat(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: str = "You are EDITH, a helpful AI assistant that analyzes notes and provides comprehensive summaries.",
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Have a chat interaction with the model
        
        Args:
            message: User message
            context: Optional context from vector store
            system_prompt: System prompt for the model
            max_tokens: Override max tokens for this specific chat
            
        Returns:
            Model response
        """
        prompt = self.create_prompt(system_prompt, message, context)
        response = self.generate_text(prompt, max_tokens=max_tokens)
        return response