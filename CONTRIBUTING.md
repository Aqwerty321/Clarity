# Contributing to Clarity

Thank you for your interest in contributing to Clarity! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/clarity.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Commit with meaningful messages: `git commit -m "feat: add new feature"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a pull request

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Local Development

1. **Backend Setup**
   ```bash
   cd local_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 5000
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in Auth0 credentials

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Run linter: `ruff check .`
- Format with: `black .`
- Maximum line length: 100

### JavaScript/Vue (Frontend)

- Follow ESLint rules
- Use Prettier for formatting
- Run linter: `npm run lint`
- Maximum line length: 100

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add quiz difficulty selector`

## Testing

### Backend Tests

```bash
cd local_backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Run All Tests

```bash
# From project root
pytest local_backend/tests/
cd frontend && npm run test
```

## Pull Request Process

1. **Update Documentation**: Update README.md and other docs if needed
2. **Add Tests**: Include tests for new features
3. **Run Tests**: Ensure all tests pass
4. **Update Changelog**: Add entry to CHANGELOG.md (if exists)
5. **Review**: Request review from maintainers
6. **CI/CD**: Ensure GitHub Actions pass

## Areas for Contribution

### High Priority

- [ ] Real LLM integration (gpt-oss, Ollama)
- [ ] Scholar API integration (arXiv, PubMed)
- [ ] Spaced repetition algorithm for flashcards
- [ ] Mobile app (React Native or Flutter)
- [ ] Real-time collaboration

### Medium Priority

- [ ] More embedding models
- [ ] Advanced quiz generation
- [ ] Export to Anki/Quizlet
- [ ] Voice input (Whisper integration)
- [ ] Multi-modal support (images in documents)

### Good First Issues

- [ ] UI improvements
- [ ] Documentation enhancements
- [ ] Additional unit tests
- [ ] Bug fixes
- [ ] Translation/i18n

## Code Review Guidelines

Reviewers will check for:

- Code quality and readability
- Test coverage
- Documentation updates
- Performance implications
- Security considerations
- Accessibility (frontend)

## Community

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Discord**: [Join our Discord](https://discord.gg/clarity) (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or reach out to the maintainers.

Thank you for contributing to Clarity! 🎉
