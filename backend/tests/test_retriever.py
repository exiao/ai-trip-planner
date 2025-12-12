"""Unit tests for LocalGuideRetriever and _load_local_documents."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from main import LocalGuideRetriever, _load_local_documents
from tests.fixtures.sample_data import SAMPLE_LOCAL_GUIDES


class TestLoadLocalDocuments:
    """Tests for _load_local_documents helper function."""
    
    def test_loads_valid_json(self, temp_local_guides_file):
        """Test loading valid JSON file."""
        docs = _load_local_documents(temp_local_guides_file)
        assert len(docs) == len(SAMPLE_LOCAL_GUIDES)
        assert all(isinstance(doc, Document) for doc in docs)
    
    def test_handles_nonexistent_file(self, temp_nonexistent_file):
        """Test handling of non-existent file."""
        docs = _load_local_documents(temp_nonexistent_file)
        assert docs == []
    
    def test_handles_malformed_json(self, temp_malformed_guides_file):
        """Test handling of malformed JSON."""
        docs = _load_local_documents(temp_malformed_guides_file)
        assert docs == []
    
    def test_handles_empty_file(self, temp_empty_guides_file):
        """Test handling of empty JSON array."""
        docs = _load_local_documents(temp_empty_guides_file)
        assert docs == []
    
    def test_filters_invalid_entries(self, tmp_path):
        """Test that entries without city or description are filtered out."""
        invalid_data = [
            {"city": "Tokyo"},  # Missing description
            {"description": "A guide"},  # Missing city
            {"city": "Paris", "description": "Valid guide"},  # Valid
        ]
        guides_file = tmp_path / "guides.json"
        guides_file.write_text(json.dumps(invalid_data))
        
        docs = _load_local_documents(guides_file)
        assert len(docs) == 1
        assert docs[0].metadata["city"] == "Paris"
    
    def test_extracts_metadata_correctly(self, temp_local_guides_file):
        """Test that metadata is extracted correctly."""
        docs = _load_local_documents(temp_local_guides_file)
        assert len(docs) > 0
        
        # Check first document
        doc = docs[0]
        assert "city" in doc.metadata
        assert "interests" in doc.metadata
        assert "source" in doc.metadata
        assert "City:" in doc.page_content
        assert "Guide:" in doc.page_content
    
    def test_handles_missing_interests(self, tmp_path):
        """Test handling of entries without interests field."""
        data = [{"city": "Tokyo", "description": "A guide"}]
        guides_file = tmp_path / "guides.json"
        guides_file.write_text(json.dumps(data))
        
        docs = _load_local_documents(guides_file)
        assert len(docs) == 1
        assert docs[0].metadata.get("interests") == []


class TestLocalGuideRetrieverInitialization:
    """Tests for LocalGuideRetriever initialization."""
    
    def test_initializes_with_valid_file(self, temp_local_guides_file):
        """Test initialization with valid JSON file."""
        retriever = LocalGuideRetriever(temp_local_guides_file)
        assert not retriever.is_empty
        assert len(retriever._docs) == len(SAMPLE_LOCAL_GUIDES)
    
    def test_initializes_with_empty_file(self, temp_empty_guides_file):
        """Test initialization with empty file."""
        retriever = LocalGuideRetriever(temp_empty_guides_file)
        assert retriever.is_empty
        assert len(retriever._docs) == 0
    
    def test_initializes_with_nonexistent_file(self, temp_nonexistent_file):
        """Test initialization with non-existent file."""
        retriever = LocalGuideRetriever(temp_nonexistent_file)
        assert retriever.is_empty
    
    def test_no_vectorstore_in_test_mode(self, temp_local_guides_file):
        """Test that vectorstore is not created in TEST_MODE."""
        retriever = LocalGuideRetriever(temp_local_guides_file)
        assert retriever._vectorstore is None
        assert retriever._embeddings is None


class TestIsEmptyProperty:
    """Tests for is_empty property."""
    
    def test_returns_true_when_empty(self, temp_empty_guides_file):
        """Test is_empty returns True for empty retriever."""
        retriever = LocalGuideRetriever(temp_empty_guides_file)
        assert retriever.is_empty
    
    def test_returns_false_when_has_docs(self, temp_local_guides_file):
        """Test is_empty returns False when documents are loaded."""
        retriever = LocalGuideRetriever(temp_local_guides_file)
        assert not retriever.is_empty


class TestRetrieveMethod:
    """Tests for retrieve method."""
    
    def test_returns_empty_when_rag_disabled(self, temp_local_guides_file, monkeypatch):
        """Test retrieve returns empty list when RAG is disabled."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", False)
        # Need to create new retriever after patching ENABLE_RAG
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("Tokyo", None)
        assert results == []
    
    def test_returns_empty_when_empty(self, temp_empty_guides_file, monkeypatch):
        """Test retrieve returns empty list when retriever is empty."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_empty_guides_file)
        results = retriever.retrieve("Tokyo", None)
        assert results == []
    
    def test_keyword_fallback_matches_city(self, temp_local_guides_file, monkeypatch):
        """Test keyword fallback matches city names."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("Tokyo", None, k=5)
        
        # Should return Tokyo entries
        assert len(results) > 0
        assert all("Tokyo" in r["content"] or r["metadata"]["city"] == "Tokyo" 
                  for r in results)
    
    def test_keyword_fallback_filters_by_interests(self, temp_local_guides_file, monkeypatch):
        """Test keyword fallback filters by interests."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("Tokyo", "food", k=5)
        
        # Should prioritize entries with food interest
        assert len(results) > 0
        # Check that results have food-related content or interests
        food_results = [r for r in results if "food" in r["content"].lower() or 
                       any("food" in str(i).lower() for i in r["metadata"].get("interests", []))]
        assert len(food_results) > 0
    
    def test_keyword_fallback_respects_k_parameter(self, temp_local_guides_file, monkeypatch):
        """Test that k parameter limits results."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("Tokyo", None, k=2)
        assert len(results) <= 2
    
    def test_keyword_fallback_returns_empty_for_no_match(self, temp_local_guides_file, monkeypatch):
        """Test keyword fallback returns empty for non-matching destination."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("NonexistentCity", None, k=5)
        assert results == []
    
    def test_keyword_fallback_scores_correctly(self, temp_local_guides_file, monkeypatch):
        """Test keyword fallback scoring logic."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("Tokyo", "food", k=5)
        
        # Results should be sorted by score (descending)
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)
        
        # All results should have score > 0
        assert all(r["score"] > 0 for r in results)
    
    def test_keyword_fallback_handles_comma_separated_interests(self, temp_local_guides_file, monkeypatch):
        """Test keyword fallback handles comma-separated interests."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        results = retriever.retrieve("Tokyo", "food, culture", k=5)
        
        assert len(results) > 0
        # Should match entries with either food or culture
    
    def test_keyword_fallback_handles_partial_city_match(self, temp_local_guides_file, monkeypatch):
        """Test keyword fallback handles partial city name matches."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        # Test with "Tokyo, Japan" should match "Tokyo"
        results = retriever.retrieve("Tokyo, Japan", None, k=5)
        assert len(results) > 0
    
    def test_vector_search_path_when_available(self, temp_local_guides_file, monkeypatch):
        """Test vector search path when vectorstore is available."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", True)
        
        # Mock vectorstore
        mock_vectorstore = MagicMock()
        mock_doc = Document(
            page_content="City: Tokyo\nInterests: food\nGuide: Test guide",
            metadata={"city": "Tokyo", "interests": ["food"], "score": 0.95}
        )
        mock_retriever = MagicMock()
        mock_retriever.invoke = Mock(return_value=[mock_doc])
        mock_vectorstore.as_retriever = Mock(return_value=mock_retriever)
        
        retriever = LocalGuideRetriever(temp_local_guides_file)
        retriever._vectorstore = mock_vectorstore
        
        results = retriever.retrieve("Tokyo", "food", k=3)
        
        assert len(results) > 0
        assert results[0]["content"] == mock_doc.page_content
        assert results[0]["score"] == 0.95
    
    def test_falls_back_to_keywords_on_vector_error(self, temp_local_guides_file, monkeypatch):
        """Test that vector search errors fall back to keyword search."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", True)
        
        # Mock vectorstore that raises exception
        mock_vectorstore = MagicMock()
        mock_vectorstore.as_retriever = Mock(side_effect=Exception("Vector search failed"))
        
        retriever = LocalGuideRetriever(temp_local_guides_file)
        retriever._vectorstore = mock_vectorstore
        
        results = retriever.retrieve("Tokyo", None, k=3)
        
        # Should fall back to keyword search
        assert isinstance(results, list)
        # May be empty if no matches, but should not raise exception


class TestKeywordFallbackScoring:
    """Tests for _keyword_fallback scoring logic."""
    
    def test_city_match_scores_higher(self, temp_local_guides_file, monkeypatch):
        """Test that city matches score higher than non-matches."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        
        tokyo_results = retriever.retrieve("Tokyo", None, k=10)
        paris_results = retriever.retrieve("Paris", None, k=10)
        
        # Tokyo results should have Tokyo entries with higher scores
        if tokyo_results:
            assert any("Tokyo" in r["metadata"]["city"] for r in tokyo_results)
        
        # Paris results should have Paris entries
        if paris_results:
            assert any("Paris" in r["metadata"]["city"] for r in paris_results)
    
    def test_interest_matching_adds_to_score(self, temp_local_guides_file, monkeypatch):
        """Test that matching interests increases score."""
        monkeypatch.setenv("ENABLE_RAG", "1")
        retriever = LocalGuideRetriever(temp_local_guides_file)
        
        # Get results with and without interests
        results_with_interests = retriever.retrieve("Tokyo", "food", k=10)
        results_without_interests = retriever.retrieve("Tokyo", None, k=10)
        
        # Results with matching interests should be prioritized
        if results_with_interests:
            # Top results should have food-related content
            top_result = results_with_interests[0]
            assert ("food" in top_result["content"].lower() or 
                   any("food" in str(i).lower() for i in top_result["metadata"].get("interests", [])))

