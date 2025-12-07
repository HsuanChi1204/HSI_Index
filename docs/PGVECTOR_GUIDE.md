# How to Use pgvector with Supabase

This guide explains how to set up and use `pgvector` for storing and querying vector embeddings in your Supabase database.

## 1. Enable the Extension
Run this SQL command in your Supabase SQL Editor to enable the vector extension:
```sql
create extension if not exists vector;
```

## 2. Create a Documents Table
Create a table to store your text chunks and their embeddings.
```sql
create table documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(768) -- Dimension depends on the model (Gemini uses 768)
);
```

## 3. Create a Similarity Search Function
Create a PostgreSQL function to find the most similar documents.
```sql
create or replace function match_documents (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

## 4. Python Implementation (Using `vecs` or direct SQL)
You can use the `supabase` python client to insert and query.

### Inserting Data
```python
import google.generativeai as genai

# Generate embedding
result = genai.embed_content(
    model="models/text-embedding-004",
    content="Your text content here",
    task_type="retrieval_document"
)
embedding = result['embedding']

# Insert into Supabase
supabase.table('documents').insert({
    'content': "Your text content here",
    'embedding': embedding
}).execute()
```

### Querying Data
```python
# Generate query embedding
result = genai.embed_content(
    model="models/text-embedding-004",
    content="User query here",
    task_type="retrieval_query"
)
query_embedding = result['embedding']

# Call the RPC function
response = supabase.rpc(
    'match_documents',
    {
        'query_embedding': query_embedding,
        'match_threshold': 0.7,
        'match_count': 5
    }
).execute()

for doc in response.data:
    print(f"Found: {doc['content']} (Sim: {doc['similarity']})")
```
