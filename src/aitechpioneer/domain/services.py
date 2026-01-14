import difflib
from typing import Any, Dict, List, Optional

from .models import (
    Chunk,
    EffectRating,
    RetrievedChunkInfo,
    RootCause,
    VerificationRecord,
)
from .ports import EmbeddingServicePort


class EmbeddingService:
    def __init__(self, embedding_port: EmbeddingServicePort):
        self._embedding_port = embedding_port

    async def generate_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        return await self._embedding_port.generate_embedding(text)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            raise ValueError("No valid texts provided")

        return await self._embedding_port.generate_embeddings(valid_texts)

    async def generate_chunk_embedding(self, chunk: Chunk) -> Chunk:
        if not chunk.content:
            raise ValueError("Chunk content cannot be empty")

        embedding = await self.generate_embedding(chunk.content)
        chunk.update_embedding(embedding)
        return chunk

    async def generate_chunks_embeddings(self, chunks: List[Chunk]) -> List[Chunk]:
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks if chunk.content]
        if not texts:
            raise ValueError("No valid chunks provided")

        embeddings = await self.generate_embeddings(texts)

        result_chunks = []
        embedding_index = 0
        for chunk in chunks:
            if chunk.content:
                chunk.update_embedding(embeddings[embedding_index])
                embedding_index += 1
            result_chunks.append(chunk)

        return result_chunks

    def get_embedding_size(self) -> int:
        return self._embedding_port.get_embedding_size()


class SimilarityService:
    def __init__(self, embedding_port: EmbeddingServicePort):
        self._embedding_port = embedding_port

    async def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        try:
            embedding1 = await self._embedding_port.generate_embedding(text1)
            embedding2 = await self._embedding_port.generate_embedding(text2)

            return self._cosine_similarity(embedding1, embedding2)
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()

    async def calculate_combined_similarity(
        self, text1: str, text2: str, semantic_weight: float = 0.7
    ) -> float:
        if semantic_weight < 0 or semantic_weight > 1:
            raise ValueError("Semantic weight must be between 0 and 1")

        semantic_sim = await self.calculate_semantic_similarity(text1, text2)
        text_sim = self.calculate_text_similarity(text1, text2)

        combined = semantic_weight * semantic_sim + (1 - semantic_weight) * text_sim
        return combined

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def calculate_chunks_similarity(
        self, chunks1: List[RetrievedChunkInfo], chunks2: List[RetrievedChunkInfo]
    ) -> Dict[str, Any]:
        if not chunks1 or not chunks2:
            return {
                "similarity": 0.0,
                "added": len(chunks2),
                "removed": len(chunks1),
                "same": 0,
                "changed": 0,
            }

        chunk_ids1 = {c.chunk_id for c in chunks1}
        chunk_ids2 = {c.chunk_id for c in chunks2}

        added = len(chunk_ids2 - chunk_ids1)
        removed = len(chunk_ids1 - chunk_ids2)
        same = len(chunk_ids1 & chunk_ids2)
        changed = 0

        for chunk_id in chunk_ids1 & chunk_ids2:
            chunk1 = next(c for c in chunks1 if c.chunk_id == chunk_id)
            chunk2 = next(c for c in chunks2 if c.chunk_id == chunk_id)
            if chunk1.content != chunk2.content:
                changed += 1

        total_chunks = len(chunks1) + len(chunks2)
        similarity = (same * 2) / total_chunks if total_chunks > 0 else 0.0

        return {
            "similarity": similarity,
            "added": added,
            "removed": removed,
            "same": same,
            "changed": changed,
        }

    async def calculate_score_changes(
        self, chunks1: List[RetrievedChunkInfo], chunks2: List[RetrievedChunkInfo]
    ) -> Dict[str, float]:
        if not chunks1 or not chunks2:
            return {
                "original_avg": 0.0,
                "new_avg": 0.0,
                "improvement": 0.0,
            }

        original_avg = sum(c.score for c in chunks1) / len(chunks1)
        new_avg = sum(c.score for c in chunks2) / len(chunks2)
        improvement = new_avg - original_avg

        return {
            "original_avg": original_avg,
            "new_avg": new_avg,
            "improvement": improvement,
        }


class ComparisonService:
    def __init__(self, similarity_service: SimilarityService):
        self._similarity_service = similarity_service

    async def compare_answers(
        self, original_answer: str, new_answer: str
    ) -> Dict[str, Any]:
        similarity = await self._similarity_service.calculate_combined_similarity(
            original_answer, new_answer
        )

        return {
            "similarity": similarity,
            "original_length": len(original_answer),
            "new_length": len(new_answer),
            "length_diff": len(new_answer) - len(original_answer),
        }

    async def compare_chunks(
        self, original_chunks: List[RetrievedChunkInfo], new_chunks: List[RetrievedChunkInfo]
    ) -> Dict[str, Any]:
        chunk_changes = await self._similarity_service.calculate_chunks_similarity(
            original_chunks, new_chunks
        )
        score_changes = await self._similarity_service.calculate_score_changes(
            original_chunks, new_chunks
        )

        return {
            "chunk_changes": chunk_changes,
            "score_changes": score_changes,
        }

    async def evaluate_optimization_effect(
        self,
        original_answer: str,
        new_answer: str,
        original_chunks: List[RetrievedChunkInfo],
        new_chunks: List[RetrievedChunkInfo],
    ) -> Dict[str, Any]:
        answer_comparison = await self.compare_answers(original_answer, new_answer)
        chunks_comparison = await self.compare_chunks(original_chunks, new_chunks)

        similarity = answer_comparison["similarity"]
        score_improvement = chunks_comparison["score_changes"]["improvement"]

        effect_rating = self._determine_effect_rating(similarity, score_improvement)

        return {
            "answer_similarity": similarity,
            "chunk_similarity": chunks_comparison["chunk_changes"]["similarity"],
            "score_improvement": score_improvement,
            "effect_rating": effect_rating,
            "answer_comparison": answer_comparison,
            "chunks_comparison": chunks_comparison,
        }

    def _determine_effect_rating(
        self, similarity: float, score_improvement: float
    ) -> EffectRating:
        if similarity > 0.8 and score_improvement > 0.1:
            return EffectRating.BETTER
        elif similarity < 0.5 or score_improvement < -0.1:
            return EffectRating.WORSE
        else:
            return EffectRating.SAME

    async def create_verification_record(
        self,
        question_id: str,
        test_plan_id: str,
        original_answer: str,
        new_answer: str,
        original_chunks: List[RetrievedChunkInfo],
        new_chunks: List[RetrievedChunkInfo],
        user_comment: Optional[str] = None,
    ) -> VerificationRecord:
        evaluation = await self.evaluate_optimization_effect(
            original_answer, new_answer, original_chunks, new_chunks
        )

        verification = VerificationRecord(
            question_id=question_id,
            test_plan_id=test_plan_id,
            original_answer=original_answer,
            new_answer=new_answer,
            original_chunks=original_chunks,
            new_chunks=new_chunks,
            similarity_score=evaluation["answer_similarity"],
            chunk_changes=evaluation["chunks_comparison"]["chunk_changes"],
            score_changes=evaluation["chunks_comparison"]["score_changes"],
            effect_rating=evaluation["effect_rating"],
            user_comment=user_comment,
        )

        return verification


class RootCauseAnalysisService:
    def __init__(self):
        pass

    async def analyze_question_root_cause(
        self,
        question: str,
        answer: str,
        retrieved_chunks: List[RetrievedChunkInfo],
    ) -> Dict[str, Any]:
        analysis = {
            "possible_causes": [],
            "related_chunks": [],
            "optimization_suggestions": [],
            "confidence": 0.0,
        }

        if not retrieved_chunks:
            analysis["possible_causes"].append({
                "cause": "no_retrieved_chunks",
                "description": "No chunks were retrieved for the question",
                "severity": "high",
            })
            analysis["optimization_suggestions"].append({
                "type": "adjust_retrieval_params",
                "description": "Adjust retrieval parameters (top_k, score_threshold)",
            })
            return analysis

        avg_score = sum(c.score for c in retrieved_chunks) / len(retrieved_chunks)
        low_score_chunks = [c for c in retrieved_chunks if c.score < 0.5]

        if avg_score < 0.5:
            analysis["possible_causes"].append({
                "cause": "low_retrieval_score",
                "description": f"Average retrieval score is low ({avg_score:.2f})",
                "severity": "medium",
            })
            analysis["optimization_suggestions"].append({
                "type": "improve_chunk_quality",
                "description": "Improve chunk content quality and relevance",
            })

        if low_score_chunks:
            analysis["possible_causes"].append({
                "cause": "irrelevant_chunks",
                "description": f"{len(low_score_chunks)} chunks have low relevance scores",
                "severity": "medium",
            })
            analysis["related_chunks"].extend([c.chunk_id for c in low_score_chunks])
            analysis["optimization_suggestions"].append({
                "type": "merge_chunks",
                "description": "Consider merging chunks to improve context",
                "chunk_ids": [c.chunk_id for c in low_score_chunks],
            })

        for chunk in retrieved_chunks:
            if len(chunk.content) < 100:
                analysis["possible_causes"].append({
                    "cause": "chunk_too_small",
                    "description": (
                        f"Chunk {chunk.chunk_id} is too small "
                        f"({len(chunk.content)} chars)"
                    ),
                    "severity": "medium",
                })
                analysis["related_chunks"].append(chunk.chunk_id)
                analysis["optimization_suggestions"].append({
                    "type": "merge_chunks",
                    "description": f"Merge chunk {chunk.chunk_id} with adjacent chunks",
                    "chunk_ids": [chunk.chunk_id],
                })
            elif len(chunk.content) > 2000:
                analysis["possible_causes"].append({
                    "cause": "chunk_too_large",
                    "description": (
                        f"Chunk {chunk.chunk_id} is too large "
                        f"({len(chunk.content)} chars)"
                    ),
                    "severity": "medium",
                })
                analysis["related_chunks"].append(chunk.chunk_id)
                analysis["optimization_suggestions"].append({
                    "type": "split_chunk",
                    "description": f"Split chunk {chunk.chunk_id} into smaller chunks",
                    "chunk_ids": [chunk.chunk_id],
                })

        if not analysis["possible_causes"]:
            analysis["possible_causes"].append({
                "cause": "unknown",
                "description": "Unable to determine root cause",
                "severity": "low",
            })

        analysis["confidence"] = self._calculate_confidence(analysis["possible_causes"])
        analysis["related_chunks"] = list(set(analysis["related_chunks"]))

        return analysis

    def _calculate_confidence(self, causes: List[Dict[str, Any]]) -> float:
        if not causes:
            return 0.0

        severity_weights = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4,
        }

        total_weight = sum(severity_weights.get(c["severity"], 0.5) for c in causes)
        confidence = total_weight / len(causes)

        return min(confidence, 1.0)

    def map_cause_to_root_cause(self, cause: str) -> RootCause:
        cause_mapping = {
            "chunk_too_small": RootCause.CHUNK_TOO_SMALL,
            "chunk_too_large": RootCause.CHUNK_TOO_LARGE,
            "irrelevant_chunks": RootCause.BOUNDARY_ISSUE,
            "low_retrieval_score": RootCause.BOUNDARY_ISSUE,
            "no_retrieved_chunks": RootCause.INCOMPLETE_CONTENT,
        }

        return cause_mapping.get(cause, RootCause.OTHER)



