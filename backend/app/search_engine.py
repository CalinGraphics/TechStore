"""Simple IR search engine for products and specification documents.

This module implements:
- tokenization
- TF-IDF vector scoring
- BM25 scoring (Lucene-style approximation)
- cosine similarity between TF-IDF vectors

It works fully in-memory and is optimized for the small/medium collections
used in this project (hardcoded products / Supabase-backed products).
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


TOKEN_RE = re.compile(r"[A-Za-z0-9]+", re.UNICODE)


def tokenize(text: str) -> List[str]:
    """Tokenize text into normalized terms."""
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text or "")]


def build_document_text(product: dict) -> str:
    """Build a concatenated text representation of a product for indexing."""
    parts: List[str] = []
    parts.append(str(product.get("name", "")))
    parts.append(str(product.get("description", "")))
    parts.append(str(product.get("category", "")))
    parts.append(str(product.get("brand", "")))

    tags = product.get("tags") or []
    if isinstance(tags, (list, tuple)):
        parts.extend(str(tag) for tag in tags)

    specs = product.get("specs") or {}
    if isinstance(specs, dict):
        for key, value in specs.items():
            parts.append(str(key))
            parts.append(str(value))

    return " ".join(parts)


def build_spec_text(product: dict) -> str:
    """Build a specification-focused document text for Lucene-style search."""
    specs = product.get("specs") or {}
    lines: List[str] = []
    if isinstance(specs, dict):
        for key, value in specs.items():
            lines.append(f"{key}: {value}")
    # Include description as specification context
    description = product.get("description")
    if description:
        lines.append(description)
    return "\n".join(lines)


@dataclass
class IndexedDocument:
    doc_id: str
    product_id: str
    length: int
    term_freqs: Counter


@dataclass
class SearchResult:
    product_id: str
    score: float
    snippet: str | None = None


class InMemoryIndex:
    """In-memory inverted index supporting TF-IDF and BM25 scoring."""

    def __init__(self) -> None:
        self.documents: Dict[str, IndexedDocument] = {}
        self.inverted_index: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.doc_count: int = 0
        self.avg_doc_len: float = 0.0

    def index_documents(self, docs: Iterable[Tuple[str, str]]) -> None:
        """(Re)build index from iterable of (product_id, text)."""
        self.documents.clear()
        self.inverted_index.clear()

        total_len = 0
        for idx, (product_id, text) in enumerate(docs):
            doc_id = str(idx)
            tokens = tokenize(text)
            tf = Counter(tokens)
            length = sum(tf.values())
            total_len += length or 1

            indexed = IndexedDocument(
                doc_id=doc_id,
                product_id=product_id,
                length=length or 1,
                term_freqs=tf,
            )
            self.documents[doc_id] = indexed

            for term, freq in tf.items():
                self.inverted_index[term][doc_id] = freq

        self.doc_count = len(self.documents)
        self.avg_doc_len = (total_len / self.doc_count) if self.doc_count else 0.0

    # --- IDF helpers (Lucene-style approximations) ---

    def _idf_tfidf(self, term: str) -> float:
        """IDF for TF-IDF scoring (log((N + 1) / (df + 1)))."""
        df = len(self.inverted_index.get(term, {}))
        if df == 0 or self.doc_count == 0:
            return 0.0
        return math.log((self.doc_count + 1) / (df + 1))

    def _idf_bm25(self, term: str) -> float:
        """IDF for BM25, using standard BM25 formula.

        idf = log(1 + (N - df + 0.5) / (df + 0.5))
        """
        df = len(self.inverted_index.get(term, {}))
        if df == 0 or self.doc_count == 0:
            return 0.0
        return math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))

    # --- Scoring methods ---

    def search_tfidf(self, query: str, top_k: int = 20) -> List[SearchResult]:
        """Score documents using TF-IDF and return top_k results."""
        query_terms = tokenize(query)
        if not query_terms or self.doc_count == 0:
            return []

        scores: Dict[str, float] = defaultdict(float)
        for term in query_terms:
            postings = self.inverted_index.get(term)
            if not postings:
                continue
            idf = self._idf_tfidf(term)
            for doc_id, tf in postings.items():
                # log-normalized term frequency
                tf_weight = 1.0 + math.log(tf)
                scores[doc_id] += tf_weight * idf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            SearchResult(
                product_id=self.documents[doc_id].product_id,
                score=score,
            )
            for doc_id, score in ranked
        ]

    def search_bm25(
        self, query: str, top_k: int = 20, k1: float = 1.5, b: float = 0.75
    ) -> List[SearchResult]:
        """Score documents using BM25 and return top_k results."""
        query_terms = tokenize(query)
        if not query_terms or self.doc_count == 0:
            return []

        scores: Dict[str, float] = defaultdict(float)
        for term in query_terms:
            postings = self.inverted_index.get(term)
            if not postings:
                continue
            idf = self._idf_bm25(term)
            for doc_id, tf in postings.items():
                doc = self.documents[doc_id]
                denom = tf + k1 * (1.0 - b + b * (doc.length / (self.avg_doc_len or 1.0)))
                weight = idf * (tf * (k1 + 1.0)) / (denom or 1.0)
                scores[doc_id] += weight

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            SearchResult(
                product_id=self.documents[doc_id].product_id,
                score=score,
            )
            for doc_id, score in ranked
        ]

    # --- Vector helpers for cosine similarity ---

    def build_tfidf_vector(self, doc: IndexedDocument) -> Dict[str, float]:
        """Build TF-IDF vector for a document."""
        vec: Dict[str, float] = {}
        for term, tf in doc.term_freqs.items():
            idf = self._idf_tfidf(term)
            if idf == 0.0:
                continue
            tf_weight = 1.0 + math.log(tf)
            vec[term] = tf_weight * idf
        return vec

    def cosine_similarity(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors."""
        if not a or not b:
            return 0.0
        # Ensure iteration over smaller dict for efficiency
        if len(a) > len(b):
            a, b = b, a

        dot = 0.0
        for term, aval in a.items():
            bval = b.get(term)
            if bval is not None:
                dot += aval * bval

        if dot == 0.0:
            return 0.0

        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


def build_product_index(products: List[dict]) -> InMemoryIndex:
    """Convenience helper to build index from products."""
    index = InMemoryIndex()
    docs = [(p["id"], build_document_text(p)) for p in products]
    index.index_documents(docs)
    return index


def build_spec_index(products: List[dict]) -> InMemoryIndex:
    """Build index that focuses on technical specifications of products."""
    index = InMemoryIndex()
    docs = [(p["id"], build_spec_text(p)) for p in products]
    index.index_documents(docs)
    return index

