# Clarity Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-01

### Added
- Initial release of Clarity
- Vue 3 frontend with Tailwind CSS and Auth0 authentication
- Local FastAPI backend with RAG pipeline
- ChromaDB vector storage for embeddings
- Sentence-transformers embedding support (all-MiniLM-L6-v2)
- Document ingestion (PDF, TXT, Markdown)
- Text chunking with configurable size and overlap
- Question answering with RAG
- Quiz generation from documents
- Mock LLM wrapper (extensible for real models)
- Cloud sync backend for Render deployment
- PostgreSQL integration for notebook persistence
- Docker and docker-compose support
- GitHub Actions CI/CD pipeline
- Comprehensive documentation
- Demo data and seed script
- Unit tests for backend and frontend

### Features
- **Privacy-first**: All AI inference runs locally
- **Cross-platform**: Works on Windows, macOS, Linux
- **Extensible**: Easy to swap LLM providers
- **Production-ready**: Docker, CI/CD, tests included
- **Demo-ready**: Sample data and startup scripts

## [Unreleased]

### Planned
- Real LLM integration (gpt-oss, Ollama, OpenAI)
- Scholar API integration (arXiv, PubMed)
- Spaced repetition for flashcards
- Multi-modal document support
- Voice input with Whisper
- Mobile application
- Real-time collaboration
- Advanced analytics dashboard
