"""
TF-IDF Similarity Matrix for BMIS ML Pipeline

This module builds TF-IDF vectorizer and computes similarity scores
for content-based recommendation ranking.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import save_npz, load_npz
import joblib
import os


class TFIDFSimilarityEngine:
    """TF-IDF vectorizer and similarity computation for BMIS resources"""

    def __init__(self, data_path='data/bmis_final_ml_ready_dataset_cs_refined.csv'):
        self.data_path = data_path
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.similarity_matrix = None

    def load_data(self):
        """Load dataset"""
        self.df = pd.read_csv(self.data_path)
        print(f"[OK] Loaded {len(self.df)} resources")
        return self

    def build_vectorizer(self, max_features=500, min_df=2, max_df=0.8, ngram_range=(1, 2)):
        """
        Build TF-IDF vectorizer on tfidf_text corpus

        Args:
            max_features: Maximum number of terms to keep
            min_df: Ignore terms appearing in fewer than this many documents
            max_df: Ignore terms appearing in more than this fraction of documents
            ngram_range: Range of n-grams to extract
        """
        print("\n" + "="*60)
        print("Building TF-IDF Vectorizer")
        print("="*60)

        # Check for tfidf_text column
        if 'tfidf_text' not in self.df.columns:
            raise ValueError("Column 'tfidf_text' not found in dataset")

        # Fill missing values
        corpus = self.df['tfidf_text'].fillna('').astype(str)

        print(f"Corpus size: {len(corpus)} documents")
        print(f"Average text length: {corpus.str.len().mean():.0f} characters")

        # Build vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            stop_words='english',
            strip_accents='unicode',
            lowercase=True
        )

        # Fit and transform
        print(f"\nFitting vectorizer...")
        print(f"  max_features={max_features}")
        print(f"  min_df={min_df}")
        print(f"  max_df={max_df}")
        print(f"  ngram_range={ngram_range}")

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

        print(f"\n[OK] TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        print(f"[OK] Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        print(f"[OK] Matrix density: {self.tfidf_matrix.nnz / (self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1]):.4f}")

        # Show top terms by IDF weight
        feature_names = self.vectorizer.get_feature_names_out()
        idf_scores = self.vectorizer.idf_
        top_indices = np.argsort(idf_scores)[:20]  # Lowest IDF = most common
        bottom_indices = np.argsort(idf_scores)[-20:]  # Highest IDF = most distinctive

        print(f"\nMost common terms (low IDF):")
        for idx in top_indices[:10]:
            print(f"  {feature_names[idx]}: {idf_scores[idx]:.2f}")

        print(f"\nMost distinctive terms (high IDF):")
        for idx in bottom_indices[-10:]:
            print(f"  {feature_names[idx]}: {idf_scores[idx]:.2f}")

        return self

    def compute_similarity_matrix(self):
        """Compute full pairwise cosine similarity matrix"""
        print("\n" + "="*60)
        print("Computing Similarity Matrix")
        print("="*60)

        if self.tfidf_matrix is None:
            raise ValueError("TF-IDF matrix not built. Call build_vectorizer() first.")

        print(f"Computing {self.tfidf_matrix.shape[0]}x{self.tfidf_matrix.shape[0]} similarity matrix...")

        # Compute cosine similarity (this can be memory intensive)
        # For 2,237 resources, this will be ~2237x2237 = 5M entries
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

        print(f"[OK] Similarity matrix shape: {self.similarity_matrix.shape}")

        # Analyze similarity distribution
        # Exclude diagonal (self-similarity = 1.0)
        mask = ~np.eye(self.similarity_matrix.shape[0], dtype=bool)
        similarities = self.similarity_matrix[mask]

        print(f"\nSimilarity Distribution:")
        print(f"  Mean: {similarities.mean():.3f}")
        print(f"  Median: {np.median(similarities):.3f}")
        print(f"  Std: {similarities.std():.3f}")
        print(f"  Min: {similarities.min():.3f}")
        print(f"  Max: {similarities.max():.3f}")

        # Percentiles
        percentiles = [25, 50, 75, 90, 95, 99]
        print(f"\nPercentiles:")
        for p in percentiles:
            val = np.percentile(similarities, p)
            print(f"  {p}th: {val:.3f}")

        # Count high-similarity pairs
        high_sim_threshold = 0.7
        n_high_sim = (similarities > high_sim_threshold).sum()
        print(f"\nHigh-similarity pairs (>{high_sim_threshold}): {n_high_sim} ({100*n_high_sim/len(similarities):.2f}%)")

        return self

    def get_similar_resources(self, resource_idx, top_n=10, min_similarity=0.0):
        """
        Get most similar resources to a given resource

        Args:
            resource_idx: Index of resource in dataframe
            top_n: Number of similar resources to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (index, similarity_score) tuples
        """
        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix not computed. Call compute_similarity_matrix() first.")

        # Get similarities for this resource
        sims = self.similarity_matrix[resource_idx]

        # Filter by minimum similarity and exclude self
        valid_indices = np.where((sims >= min_similarity) & (np.arange(len(sims)) != resource_idx))[0]
        valid_sims = sims[valid_indices]

        # Sort by similarity descending
        sorted_indices = np.argsort(valid_sims)[::-1][:top_n]

        results = [(valid_indices[i], valid_sims[i]) for i in sorted_indices]
        return results

    def search_by_text(self, query_text, top_n=20, min_similarity=0.0):
        """
        Search resources by text query

        Args:
            query_text: Search query text
            top_n: Number of results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (index, similarity_score, resource_name) tuples
        """
        if self.vectorizer is None or self.tfidf_matrix is None:
            raise ValueError("Vectorizer not built. Call build_vectorizer() first.")

        # Transform query text
        query_vec = self.vectorizer.transform([query_text])

        # Compute similarity with all resources
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Filter by minimum similarity
        valid_indices = np.where(similarities >= min_similarity)[0]
        valid_sims = similarities[valid_indices]

        # Sort by similarity descending
        sorted_indices = np.argsort(valid_sims)[::-1][:top_n]

        results = []
        for i in sorted_indices:
            idx = valid_indices[i]
            sim = valid_sims[i]
            name = self.df.iloc[idx]['name'] if 'name' in self.df.columns else f"Resource {idx}"
            results.append((idx, sim, name))

        return results

    def save_models(self, output_dir='models'):
        """Save vectorizer and similarity matrix"""
        os.makedirs(output_dir, exist_ok=True)

        # Save vectorizer
        joblib.dump(self.vectorizer, f'{output_dir}/tfidf_vectorizer.pkl')
        print(f"[OK] Saved vectorizer to {output_dir}/tfidf_vectorizer.pkl")

        # Save TF-IDF matrix (sparse)
        save_npz(f'{output_dir}/tfidf_matrix.npz', self.tfidf_matrix)
        print(f"[OK] Saved TF-IDF matrix to {output_dir}/tfidf_matrix.npz")

        # Save similarity matrix (dense - can be large)
        # For 2237 resources: 2237*2237*8 bytes = ~40 MB
        np.save(f'{output_dir}/similarity_matrix.npy', self.similarity_matrix)
        print(f"[OK] Saved similarity matrix to {output_dir}/similarity_matrix.npy")

        return self

    def load_models(self, output_dir='models'):
        """Load saved vectorizer and matrices"""
        self.vectorizer = joblib.load(f'{output_dir}/tfidf_vectorizer.pkl')
        self.tfidf_matrix = load_npz(f'{output_dir}/tfidf_matrix.npz')
        self.similarity_matrix = np.load(f'{output_dir}/similarity_matrix.npy')
        print(f"[OK] Loaded models from {output_dir}/")
        return self

    def validate_high_similarity_pairs(self, threshold=0.7, n_samples=10):
        """
        Validate high-similarity pairs by examining actual content

        Args:
            threshold: Similarity threshold for "high similarity"
            n_samples: Number of pairs to sample and display
        """
        print("\n" + "="*60)
        print(f"Validating High-Similarity Pairs (threshold={threshold})")
        print("="*60)

        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix not computed.")

        # Find all high-similarity pairs (upper triangle only, exclude diagonal)
        n = self.similarity_matrix.shape[0]
        high_sim_pairs = []

        for i in range(n):
            for j in range(i+1, n):
                if self.similarity_matrix[i, j] >= threshold:
                    high_sim_pairs.append((i, j, self.similarity_matrix[i, j]))

        print(f"\nFound {len(high_sim_pairs)} pairs with similarity >= {threshold}")

        # Sample and display
        if len(high_sim_pairs) > n_samples:
            import random
            sampled_pairs = random.sample(high_sim_pairs, n_samples)
        else:
            sampled_pairs = high_sim_pairs

        for idx, (i, j, sim) in enumerate(sampled_pairs, 1):
            print(f"\n--- Pair {idx}: Similarity = {sim:.3f} ---")
            print(f"Resource A (idx={i}): {self.df.iloc[i]['name']}")
            if 'category_tier1' in self.df.columns:
                print(f"  Category: {self.df.iloc[i]['category_tier1']}")
            if 'stem_field_tier1' in self.df.columns:
                print(f"  STEM Field: {self.df.iloc[i]['stem_field_tier1']}")

            print(f"\nResource B (idx={j}): {self.df.iloc[j]['name']}")
            if 'category_tier1' in self.df.columns:
                print(f"  Category: {self.df.iloc[j]['category_tier1']}")
            if 'stem_field_tier1' in self.df.columns:
                print(f"  STEM Field: {self.df.iloc[j]['stem_field_tier1']}")

        return self

    def generate_analysis_report(self, output_dir='outputs'):
        """Generate TF-IDF analysis report"""
        os.makedirs(output_dir, exist_ok=True)

        report_lines = []
        report_lines.append("="*80)
        report_lines.append("BMIS TF-IDF Similarity Analysis Report")
        report_lines.append("="*80)
        report_lines.append("")

        # Vectorizer info
        report_lines.append("TF-IDF Vectorizer Configuration:")
        report_lines.append(f"  Vocabulary Size: {len(self.vectorizer.vocabulary_)}")
        report_lines.append(f"  Matrix Shape: {self.tfidf_matrix.shape}")
        report_lines.append(f"  Matrix Density: {self.tfidf_matrix.nnz / (self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1]):.4f}")
        report_lines.append("")

        # Similarity distribution
        mask = ~np.eye(self.similarity_matrix.shape[0], dtype=bool)
        similarities = self.similarity_matrix[mask]

        report_lines.append("Similarity Distribution:")
        report_lines.append(f"  Mean: {similarities.mean():.3f}")
        report_lines.append(f"  Median: {np.median(similarities):.3f}")
        report_lines.append(f"  Std: {similarities.std():.3f}")
        report_lines.append(f"  Min: {similarities.min():.3f}")
        report_lines.append(f"  Max: {similarities.max():.3f}")
        report_lines.append("")

        # Percentiles
        report_lines.append("Percentiles:")
        for p in [25, 50, 75, 90, 95, 99]:
            val = np.percentile(similarities, p)
            report_lines.append(f"  {p}th: {val:.3f}")
        report_lines.append("")

        # High-similarity pairs
        for threshold in [0.5, 0.6, 0.7, 0.8]:
            count = (similarities > threshold).sum()
            pct = 100 * count / len(similarities)
            report_lines.append(f"Pairs with similarity >{threshold}: {count} ({pct:.2f}%)")

        # Save report
        report_text = "\n".join(report_lines)
        with open(f'{output_dir}/tfidf_analysis_report.txt', 'w') as f:
            f.write(report_text)

        print(f"\n[OK] Generated TF-IDF analysis report at {output_dir}/tfidf_analysis_report.txt")
        return report_text


if __name__ == '__main__':
    print("="*80)
    print("BMIS TF-IDF Similarity Pipeline")
    print("="*80)

    # Build TF-IDF engine
    engine = TFIDFSimilarityEngine()
    engine.load_data()
    engine.build_vectorizer(max_features=500, min_df=2, max_df=0.8, ngram_range=(1, 2))
    engine.compute_similarity_matrix()

    # Validate high-similarity pairs
    engine.validate_high_similarity_pairs(threshold=0.7, n_samples=5)

    # Save models
    engine.save_models()

    # Generate report
    engine.generate_analysis_report()

    # Test search functionality
    print("\n" + "="*60)
    print("Testing Search Functionality")
    print("="*60)

    test_query = "machine learning artificial intelligence programming"
    print(f"\nQuery: '{test_query}'")
    print("Top 10 results:")

    results = engine.search_by_text(test_query, top_n=10, min_similarity=0.1)
    for idx, (resource_idx, sim, name) in enumerate(results, 1):
        print(f"  {idx}. {name} (similarity: {sim:.3f})")

    print("\n[OK] TF-IDF pipeline complete!")
