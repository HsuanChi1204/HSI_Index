import os
import time
import re
import google.generativeai as genai
from supabase import create_client
from dotenv import load_dotenv

def upload_knowledge():
    # Load env
    load_dotenv("backend/.env")
    
    # Check keys
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not all([supabase_url, supabase_key, gemini_key]):
        print("Error: Missing environment variables.")
        return

    # Initialize clients
    supabase = create_client(supabase_url, supabase_key)
    genai.configure(api_key=gemini_key)
    
    pdf_path = "Checkpoint_Chang_Li.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    print(f"🚀 Starting Semantic Chunking for {pdf_path}...")

    # 1. Upload PDF to Gemini
    print("Uploading PDF to Gemini...")
    sample_file = genai.upload_file(path=pdf_path, display_name="HCI Research Paper")
    print(f"Uploaded file: {sample_file.display_name} as {sample_file.uri}")

    # Wait for processing
    while sample_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        sample_file = genai.get_file(sample_file.name)
    print("\nFile processed.")

    # 2. Convert to Markdown
    print("Converting PDF to Structured Markdown...")
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
    
    prompt = """
    Please convert this academic paper into structured Markdown.
    
    **Requirements:**
    1.  **Headers:** Use standard Markdown headers (#, ##, ###) for all section titles (e.g., # Introduction, ## Related Work).
    2.  **Tables:** Convert all tables into Markdown tables. Preserve all data.
    3.  **Formulas:** Use LaTeX format for all math formulas (e.g., $HCI = ...$).
    4.  **Content:** Preserve all text content accurately. Do not summarize.
    5.  **Structure:** Ensure the logical flow is maintained.
    """
    
    response = model.generate_content([sample_file, prompt])
    markdown_text = response.text
    
    # Save for debug
    with open("paper_converted.md", "w") as f:
        f.write(markdown_text)
    print("Markdown saved to 'paper_converted.md'.")

    # 3. Split by Headers (Simple Semantic Chunking)
    print("Splitting content by headers...")
    chunks = []
    current_chunk = {"title": "Start", "content": ""}
    
    lines = markdown_text.split('\n')
    for line in lines:
        # Check for headers (## or ###)
        # We treat Level 1 (#) and Level 2 (##) as chunk boundaries
        if line.strip().startswith('# ') or line.strip().startswith('## '):
            # Save previous chunk if it has content
            if current_chunk["content"].strip():
                chunks.append(current_chunk)
            
            # Start new chunk
            current_chunk = {
                "title": line.strip().lstrip('#').strip(),
                "content": line + "\n"
            }
        else:
            current_chunk["content"] += line + "\n"
            
    # Append last chunk
    if current_chunk["content"].strip():
        chunks.append(current_chunk)

    print(f"Generated {len(chunks)} semantic chunks.")

    # 4. Embed and Upload
    print("Generating embeddings and uploading to Supabase...")
    
    for i, chunk in enumerate(chunks):
        try:
            # Contextualize the chunk with its title
            text_to_embed = f"Section: {chunk['title']}\n\n{chunk['content']}"
            
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text_to_embed,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
            
            data = {
                "content": text_to_embed,
                "metadata": {"source": pdf_path, "section": chunk['title']},
                "embedding": embedding
            }
            
            supabase.table("documents").insert(data).execute()
            print(f"Uploaded chunk {i+1}/{len(chunks)}: {chunk['title']}")
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")

    print("✅ Knowledge Base Update Complete!")

if __name__ == "__main__":
    upload_knowledge()
