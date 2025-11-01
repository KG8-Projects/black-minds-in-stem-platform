"""
K-Means Clustering Models for BMIS ML Pipeline

This module trains four separate K-Means models:
1. Accessibility Profile clustering
2. Academic Level clustering
3. STEM Field Focus clustering
4. Resource Format clustering
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import joblib
import os


class BMISClusteringPipeline:
    """Trains and manages all K-Means clustering models"""

    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.models = {}
        self.cluster_assignments = {}
        self.cluster_metrics = {}

    def find_optimal_k(self, X, k_range=(4, 20), model_name='model'):
        """
        Find optimal K using elbow method and silhouette analysis

        Args:
            X: Feature matrix
            k_range: Range of K values to test
            model_name: Name for labeling outputs

        Returns:
            optimal_k: Best K value
            metrics: Dict of inertias and silhouette scores
        """
        print(f"\nFinding optimal K for {model_name}...")
        print("-" * 60)

        inertias = []
        silhouette_scores_list = []
        k_values = range(k_range[0], k_range[1] + 1)

        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)

            inertia = kmeans.inertia_
            sil_score = silhouette_score(X, labels)

            inertias.append(inertia)
            silhouette_scores_list.append(sil_score)

            if k % 3 == 0:  # Print every 3rd iteration
                print(f"K={k:2d}: Inertia={inertia:8.2f}, Silhouette={sil_score:.3f}")

        # Find optimal K (best silhouette score, with minimum K >= 6)
        valid_k_indices = [i for i, k in enumerate(k_values) if k >= 6]
        valid_silhouettes = [silhouette_scores_list[i] for i in valid_k_indices]
        best_idx = valid_k_indices[np.argmax(valid_silhouettes)]
        optimal_k = list(k_values)[best_idx]

        print(f"\n[OK] Optimal K = {optimal_k} (Silhouette = {silhouette_scores_list[best_idx]:.3f})")

        metrics = {
            'k_values': list(k_values),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores_list,
            'optimal_k': optimal_k
        }

        return optimal_k, metrics

    def train_accessibility_model(self, k_range=(6, 15)):
        """Train Accessibility Profile K-Means model"""
        print("\n" + "="*60)
        print("Training Accessibility Profile Model")
        print("="*60)

        X, indices = self.preprocessor.get_accessibility_features()

        # Find optimal K
        optimal_k, metrics = self.find_optimal_k(X, k_range, 'Accessibility')

        # Train final model
        print(f"\nTraining final model with K={optimal_k}...")
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
        labels = kmeans.fit_predict(X)

        # Calculate quality metrics
        sil_score = silhouette_score(X, labels)
        db_score = davies_bouldin_score(X, labels)

        print(f"[OK] Silhouette Score: {sil_score:.3f}")
        print(f"[OK] Davies-Bouldin Index: {db_score:.3f}")

        # Store model and assignments
        self.models['accessibility'] = kmeans
        self.cluster_assignments['accessibility'] = pd.Series(labels, index=indices)
        self.cluster_metrics['accessibility'] = {
            'silhouette': sil_score,
            'davies_bouldin': db_score,
            'inertia': kmeans.inertia_,
            'n_clusters': optimal_k,
            'optimization_metrics': metrics
        }

        # Analyze clusters
        self._analyze_accessibility_clusters(labels, indices)

        return self

    def train_academic_model(self, k_range=(6, 12)):
        """Train Academic Level K-Means model"""
        print("\n" + "="*60)
        print("Training Academic Level Model")
        print("="*60)

        X, indices = self.preprocessor.get_academic_features()

        # Find optimal K
        optimal_k, metrics = self.find_optimal_k(X, k_range, 'Academic')

        # Train final model
        print(f"\nTraining final model with K={optimal_k}...")
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
        labels = kmeans.fit_predict(X)

        # Calculate quality metrics
        sil_score = silhouette_score(X, labels)
        db_score = davies_bouldin_score(X, labels)

        print(f"[OK] Silhouette Score: {sil_score:.3f}")
        print(f"[OK] Davies-Bouldin Index: {db_score:.3f}")

        # Store model and assignments
        self.models['academic'] = kmeans
        self.cluster_assignments['academic'] = pd.Series(labels, index=indices)
        self.cluster_metrics['academic'] = {
            'silhouette': sil_score,
            'davies_bouldin': db_score,
            'inertia': kmeans.inertia_,
            'n_clusters': optimal_k,
            'optimization_metrics': metrics
        }

        # Analyze clusters
        self._analyze_academic_clusters(labels, indices)

        return self

    def train_stem_field_model(self, k_range=(12, 20)):
        """Train STEM Field Focus K-Means model"""
        print("\n" + "="*60)
        print("Training STEM Field Focus Model")
        print("="*60)

        X, indices = self.preprocessor.get_stem_field_features()

        # Find optimal K
        optimal_k, metrics = self.find_optimal_k(X, k_range, 'STEM Field')

        # Train final model
        print(f"\nTraining final model with K={optimal_k}...")
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
        labels = kmeans.fit_predict(X)

        # Calculate quality metrics
        sil_score = silhouette_score(X, labels)
        db_score = davies_bouldin_score(X, labels)

        print(f"[OK] Silhouette Score: {sil_score:.3f}")
        print(f"[OK] Davies-Bouldin Index: {db_score:.3f}")

        # Store model and assignments
        self.models['stem_field'] = kmeans
        self.cluster_assignments['stem_field'] = pd.Series(labels, index=indices)
        self.cluster_metrics['stem_field'] = {
            'silhouette': sil_score,
            'davies_bouldin': db_score,
            'inertia': kmeans.inertia_,
            'n_clusters': optimal_k,
            'optimization_metrics': metrics
        }

        # Analyze clusters
        self._analyze_stem_field_clusters(labels, indices)

        return self

    def train_format_model(self, k_range=(8, 15)):
        """Train Resource Format K-Means model"""
        print("\n" + "="*60)
        print("Training Resource Format Model")
        print("="*60)

        X, indices = self.preprocessor.get_format_features()

        # Find optimal K
        optimal_k, metrics = self.find_optimal_k(X, k_range, 'Format')

        # Train final model
        print(f"\nTraining final model with K={optimal_k}...")
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
        labels = kmeans.fit_predict(X)

        # Calculate quality metrics
        sil_score = silhouette_score(X, labels)
        db_score = davies_bouldin_score(X, labels)

        print(f"[OK] Silhouette Score: {sil_score:.3f}")
        print(f"[OK] Davies-Bouldin Index: {db_score:.3f}")

        # Store model and assignments
        self.models['format'] = kmeans
        self.cluster_assignments['format'] = pd.Series(labels, index=indices)
        self.cluster_metrics['format'] = {
            'silhouette': sil_score,
            'davies_bouldin': db_score,
            'inertia': kmeans.inertia_,
            'n_clusters': optimal_k,
            'optimization_metrics': metrics
        }

        # Analyze clusters
        self._analyze_format_clusters(labels, indices)

        return self

    # ===== CLUSTER ANALYSIS METHODS =====

    def _analyze_accessibility_clusters(self, labels, indices):
        """Analyze and describe accessibility clusters"""
        print("\nCluster Analysis:")
        print("-" * 60)

        df = self.preprocessor.df.loc[indices]
        df['cluster'] = labels

        for cluster_id in range(len(np.unique(labels))):
            cluster_data = df[df['cluster'] == cluster_id]
            size = len(cluster_data)
            pct = 100 * size / len(df)

            print(f"\nCluster {cluster_id} (n={size}, {pct:.1f}%)")

            # Most common values
            print(f"  Financial Barrier: {cluster_data['financial_barrier_level_std'].mode().values[0]}")
            print(f"  Cost Category: {cluster_data['cost_category_std'].mode().values[0]}")
            print(f"  Location: {cluster_data['location_type_std'].mode().values[0]}")
            print(f"  Transportation: {cluster_data['transportation_required_std'].mode().values[0]}")

    def _analyze_academic_clusters(self, labels, indices):
        """Analyze and describe academic clusters"""
        print("\nCluster Analysis:")
        print("-" * 60)

        df = self.preprocessor.df.loc[indices]
        df['cluster'] = labels

        for cluster_id in range(len(np.unique(labels))):
            cluster_data = df[df['cluster'] == cluster_id]
            size = len(cluster_data)
            pct = 100 * size / len(df)

            print(f"\nCluster {cluster_id} (n={size}, {pct:.1f}%)")

            # Most common values
            print(f"  Prerequisite Level: {cluster_data['prerequisite_level_std'].mode().values[0]}")
            print(f"  Target Grade (avg): {cluster_data['target_grade_numeric'].mean():.1f}")
            print(f"  Time Commitment (avg): {cluster_data['time_commitment_hours'].mean():.1f} hrs")
            print(f"  Support Level: {cluster_data['support_level_std'].mode().values[0]}")

    def _analyze_stem_field_clusters(self, labels, indices):
        """Analyze and describe STEM field clusters"""
        print("\nCluster Analysis:")
        print("-" * 60)

        df = self.preprocessor.df.loc[indices]
        df['cluster'] = labels

        for cluster_id in range(len(np.unique(labels))):
            cluster_data = df[df['cluster'] == cluster_id]
            size = len(cluster_data)
            pct = 100 * size / len(df)

            print(f"\nCluster {cluster_id} (n={size}, {pct:.1f}%)")

            # Top STEM fields
            top_fields = cluster_data['stem_field_tier1'].value_counts().head(3)
            print(f"  Top STEM Fields:")
            for field, count in top_fields.items():
                print(f"    - {field}: {count} ({100*count/size:.0f}%)")

            # Top categories
            top_cats = cluster_data['category_tier1'].value_counts().head(2)
            print(f"  Top Categories: {', '.join(top_cats.index.tolist())}")

    def _analyze_format_clusters(self, labels, indices):
        """Analyze and describe format clusters"""
        print("\nCluster Analysis:")
        print("-" * 60)

        df = self.preprocessor.df.loc[indices]
        df['cluster'] = labels

        for cluster_id in range(len(np.unique(labels))):
            cluster_data = df[df['cluster'] == cluster_id]
            size = len(cluster_data)
            pct = 100 * size / len(df)

            print(f"\nCluster {cluster_id} (n={size}, {pct:.1f}%)")

            # Most common values
            top_cat = cluster_data['category_tier1'].value_counts().head(1)
            print(f"  Category: {top_cat.index[0]} ({top_cat.values[0]} resources)")
            print(f"  Time Commitment (avg): {cluster_data['time_commitment_hours'].mean():.1f} hrs")
            print(f"  Support Level: {cluster_data['support_level_std'].mode().values[0]}")

    # ===== SAVE/LOAD METHODS =====

    def save_models(self, output_dir='models'):
        """Save all trained models"""
        os.makedirs(output_dir, exist_ok=True)

        for name, model in self.models.items():
            joblib.dump(model, f'{output_dir}/{name}_kmeans.pkl')

        # Save cluster assignments
        for name, assignments in self.cluster_assignments.items():
            assignments.to_csv(f'{output_dir}/{name}_clusters.csv')

        # Save metrics
        import json
        with open(f'{output_dir}/cluster_metrics.json', 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            metrics_serializable = {}
            for model_name, metrics in self.cluster_metrics.items():
                metrics_serializable[model_name] = {
                    'silhouette': float(metrics['silhouette']),
                    'davies_bouldin': float(metrics['davies_bouldin']),
                    'inertia': float(metrics['inertia']),
                    'n_clusters': int(metrics['n_clusters'])
                }
            json.dump(metrics_serializable, f, indent=2)

        print(f"\n[OK] Saved all models to {output_dir}/")
        return self

    def generate_cluster_report(self, output_dir='outputs/cluster_analysis'):
        """Generate comprehensive cluster analysis report"""
        os.makedirs(output_dir, exist_ok=True)

        report_lines = []
        report_lines.append("="*80)
        report_lines.append("BMIS K-Means Clustering Report")
        report_lines.append("="*80)
        report_lines.append("")

        for model_name in ['accessibility', 'academic', 'stem_field', 'format']:
            if model_name not in self.cluster_metrics:
                continue

            metrics = self.cluster_metrics[model_name]
            report_lines.append(f"\n{model_name.upper()} MODEL")
            report_lines.append("-"*80)
            report_lines.append(f"Number of Clusters: {metrics['n_clusters']}")
            report_lines.append(f"Silhouette Score: {metrics['silhouette']:.3f}")
            report_lines.append(f"Davies-Bouldin Index: {metrics['davies_bouldin']:.3f}")
            report_lines.append(f"Inertia: {metrics['inertia']:.2f}")
            report_lines.append("")

            # Cluster size distribution
            labels = self.cluster_assignments[model_name]
            report_lines.append("Cluster Size Distribution:")
            for cluster_id in range(metrics['n_clusters']):
                count = (labels == cluster_id).sum()
                pct = 100 * count / len(labels)
                report_lines.append(f"  Cluster {cluster_id}: {count} resources ({pct:.1f}%)")

        # Save report
        report_text = "\n".join(report_lines)
        with open(f'{output_dir}/cluster_report.txt', 'w') as f:
            f.write(report_text)

        print(f"\n[OK] Generated cluster report at {output_dir}/cluster_report.txt")
        return report_text

    def train_all_models(self):
        """Train all four K-Means models"""
        print("\n" + "="*80)
        print("BMIS K-Means Clustering Pipeline")
        print("="*80)

        self.train_accessibility_model()
        self.train_academic_model()
        self.train_stem_field_model()
        self.train_format_model()

        print("\n" + "="*80)
        print("All Models Trained Successfully!")
        print("="*80)

        return self


if __name__ == '__main__':
    # Import and run preprocessing
    from preprocessing import BMISPreprocessor

    print("Step 1: Running preprocessing...")
    preprocessor = BMISPreprocessor()
    preprocessor.run_all_preprocessing()

    print("\n\nStep 2: Training clustering models...")
    pipeline = BMISClusteringPipeline(preprocessor)
    pipeline.train_all_models()

    print("\n\nStep 3: Saving models and generating reports...")
    pipeline.save_models()
    pipeline.generate_cluster_report()

    print("\n[OK] Complete! All models trained and saved.")
