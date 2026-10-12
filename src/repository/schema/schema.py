from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, UUID, Text, JSON
from pgvector.sqlalchemy import Vector 
from uuid import uuid4

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    
    doc_id = Column(UUID, primary_key=True, default=uuid4)
    filename = Column(String(255), nullable=False) 
    file_size = Column(Integer, nullable=False)
    pages = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    chunks = relationship("Chunk", back_populates="document")
    chat_messages = relationship("ChatMessage", back_populates="document")


class Chunk(Base):
    __tablename__ = "chunks"
    
    chunk_id = Column(UUID, primary_key=True, default=uuid4)
    chunk_number = Column(Integer, nullable=False) 
    start_char = Column(Integer, nullable=False)  
    end_char = Column(Integer, nullable=False)  
    content = Column(Text, nullable=False) 
    page_number = Column(Integer, nullable=False)
    document_id = Column(UUID, ForeignKey("documents.doc_id"), nullable=False)  # Fixed: table name
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
   
    document = relationship("Document", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk")  # Changed: singular


class Embedding(Base):
    __tablename__ = "embeddings"
    
    embedding_id = Column(UUID, primary_key=True, default=uuid4)
    chunk_id = Column(UUID, ForeignKey("chunks.chunk_id"), nullable=False)  
    vector = Column(Vector(1536), nullable=False)
    embedding_model = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    chunk = relationship("Chunk", back_populates="embeddings")  


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    chat_id = Column(UUID, primary_key=True, default=uuid4)
    doc_id = Column(UUID, ForeignKey("documents.doc_id"), nullable=False)  # Added: UUID type
    query = Column(Text, nullable=False) 
    answer = Column(Text, nullable=False) 
    citations = Column(JSON, nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
   
    document = relationship("Document", back_populates="chat_messages")

    class ErrorLog(Base):
        __tablename__ = "error_log"
        log_id = Column(UUID,primary_key = True,default= "no log data")
        file_name = Column(String,nullable= False)
        function_name = Column(String,nullable = False)
        log_data = Column(String,nullable = False)
        error_details = Column(Text,nullable = False)
        request_id = Column(String, nullable=True, index=True)
        error_code = Column(String, nullable=False)
        created_at = Column(DateTime,default=func.now())
        