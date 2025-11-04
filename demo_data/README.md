# Demo Data

This directory contains sample documents for demonstrating Clarity's capabilities.

## Files

- **machine_learning_basics.md**: Introduction to machine learning concepts, algorithms, and best practices
- **deep_learning_fundamentals.md**: Overview of deep learning, neural networks, and modern architectures

## Usage

### Manual Upload

1. Start Clarity (frontend + local backend)
2. Log in with Auth0
3. Create a new notebook
4. Upload these files through the UI

### Automated Seeding

Run the seed script to automatically ingest demo data:

```bash
cd demo_data
python seed_demo.py
```

This will:
- Create chunks from the demo documents
- Generate embeddings
- Store in ChromaDB under demo user ID

### Example Queries

Once demo data is loaded, try asking:

1. "What is machine learning?"
2. "Explain neural networks"
3. "What is gradient descent?"
4. "How do you prevent overfitting?"
5. "What are transformers in deep learning?"

### Generate Quiz

Click "Generate Quiz" and use topics like:
- "Neural Networks"
- "Gradient Descent"
- "Deep Learning Architectures"

---

**Note:** These are educational documents for demonstration purposes. For production use, upload your own learning materials.
