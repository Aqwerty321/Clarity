# PostgreSQL Setup Guide for Clarity

This guide will help you set up PostgreSQL for local persistence of notebooks and documents.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+ installed and running

## Installation Steps

### 1. Install PostgreSQL

#### Windows
Download and install from: https://www.postgresql.org/download/windows/

Or use Chocolatey:
```powershell
choco install postgresql
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Docker (All platforms)
```bash
docker run --name clarity-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v clarity-postgres-data:/var/lib/postgresql/data \
  -d postgres:15
```

### 2. Verify PostgreSQL is Running

```bash
# Check PostgreSQL status
psql --version

# Test connection (password: postgres)
psql -U postgres -h localhost -p 5432
```

### 3. Install Python Dependencies

```bash
cd local_backend
pip install -r requirements.txt
```

This will install:
- `sqlalchemy` - ORM for database operations
- `psycopg2-binary` - PostgreSQL adapter for Python

### 4. Configure Database Connection

The database connection is already configured in `.env`:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clarity_db
```

**Change the password** if you set a different one during PostgreSQL installation.

### 5. Initialize Database

Run the setup script to create the database and tables:

```bash
cd local_backend
python setup_db.py
```

This will:
1. Create the `clarity_db` database
2. Create the `notebooks` table
3. Create the `documents` table

### 6. Start the Backend

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

You should see:
```
✅ PostgreSQL database initialized
📂 ChromaDB initialized
🤖 LLM wrapper ready
✅ Server is ready!
```

## Database Schema

### `notebooks` Table
- `id` (String, Primary Key) - Unique notebook identifier
- `user_id` (String) - Auth0 user ID
- `title` (String) - Notebook title
- `description` (Text, Optional) - Notebook description
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

### `documents` Table
- `id` (String, Primary Key) - Unique document identifier
- `notebook_id` (String, Foreign Key) - Reference to notebook
- `user_id` (String) - Auth0 user ID
- `name` (String) - Document filename
- `file_path` (String) - Local file system path
- `file_type` (String) - File extension (pdf, txt, md)
- `file_size` (Integer) - File size in bytes
- `chunk_count` (Integer) - Number of text chunks
- `content_hash` (String) - SHA256 hash for deduplication
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

## API Endpoints

### Notebooks
- `POST /api/notebooks` - Create a new notebook
- `GET /api/notebooks?user_id={userId}` - Get all notebooks for a user
- `GET /api/notebooks/{notebookId}?user_id={userId}` - Get a specific notebook
- `PUT /api/notebooks/{notebookId}` - Update a notebook
- `DELETE /api/notebooks/{notebookId}?user_id={userId}` - Delete a notebook

### Documents
- `GET /api/notebooks/{notebookId}/documents?user_id={userId}` - Get all documents in a notebook
- `POST /api/notebooks/{notebookId}/documents` - Upload a document (multipart/form-data)
- `DELETE /api/notebooks/{notebookId}/documents/{documentId}?user_id={userId}` - Delete a document

## Data Storage

- **PostgreSQL**: Stores notebook/document metadata
- **ChromaDB**: Stores embeddings and chunks (in `~/.clarity/chroma`)
- **File System**: Stores original uploaded files (in `~/.clarity/uploads/{userId}/{notebookId}/`)

## Troubleshooting

### "Could not connect to server"
- Make sure PostgreSQL is running: `pg_isready` or check Docker container
- Verify port 5432 is not blocked by firewall
- Check credentials in `.env`

### "Database does not exist"
- Run `python setup_db.py` to create the database

### "Permission denied"
- Grant proper permissions to PostgreSQL user
- Or change `DATABASE_URL` to use a different user

### "Module 'psycopg2' not found"
- Install dependencies: `pip install -r requirements.txt`

## Migration from Mock Data

If you have existing notebooks in the frontend store, they will be automatically created in PostgreSQL when you:
1. Create a new notebook
2. Upload a document
3. Or perform any other action

The system will fallback to in-memory storage if PostgreSQL is unavailable.

## Backup and Restore

### Backup
```bash
pg_dump -U postgres clarity_db > clarity_backup.sql
```

### Restore
```bash
psql -U postgres clarity_db < clarity_backup.sql
```

### Backup Files
```bash
# Backup uploaded documents
tar -czf clarity_uploads_backup.tar.gz ~/.clarity/uploads/

# Backup ChromaDB
tar -czf clarity_chroma_backup.tar.gz ~/.clarity/chroma/
```

## Next Steps

- All notebooks are now persisted to PostgreSQL
- Uploaded documents are stored on the file system
- Embeddings are stored in ChromaDB
- Everything survives server restarts!
